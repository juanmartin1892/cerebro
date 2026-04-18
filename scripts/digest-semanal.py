#!/usr/bin/env python3
"""
digest-semanal.py — Genera un digest semanal por proyecto activo con noticias y papers relevantes.

Cron: 0 7 * * 1  /path/to/scripts/digest-semanal.py >> /var/log/cerebro/digest-semanal.log 2>&1
"""

import datetime
import json
import logging
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Eres un asistente de investigación experto. Tu tarea es generar resúmenes ejecutivos "
    "en español sobre el estado del arte semanal de un proyecto, basándote en noticias y "
    "papers científicos proporcionados. El resumen debe ser conciso (3-5 párrafos), "
    "destacar los avances más relevantes, identificar tendencias emergentes, y ser útil "
    "para alguien que quiere mantenerse al día con el campo. Escribe en español."
)


def parse_proyectos(index_md: str) -> list[dict]:
    """Extrae proyectos activos con carpeta y topics de la tabla del INDEX.md."""
    proyectos = []
    # Formato: | [[carpeta/README\|Nombre]] | Descripción | topic1, topic2 | fecha |
    patron = re.compile(
        r"^\|\s*\[\[([^/\]]+)/[^\]]*\]\]\s*\|[^\|]*\|\s*([^\|]+?)\s*\|",
        re.MULTILINE,
    )
    for m in patron.finditer(index_md):
        carpeta = m.group(1).strip()
        topics_raw = m.group(2).strip()
        topics = [t.strip() for t in topics_raw.split(",") if t.strip()]
        if topics:
            proyectos.append({"carpeta": carpeta, "topics": topics})
    return proyectos


def brave_search(topic: str, api_key: str, num_results: int) -> list[dict]:
    """Busca noticias recientes sobre un topic en Brave Search."""
    params = urllib.parse.urlencode({
        "q": topic,
        "count": num_results,
        "freshness": "pw",
    })
    url = f"https://api.search.brave.com/res/v1/web/search?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
    except urllib.error.URLError as e:
        raise RuntimeError(str(e.reason))

    results = []
    for item in body.get("web", {}).get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "description": item.get("description", ""),
            "source": (
                item.get("profile", {}).get("name", "")
                or item.get("meta_url", {}).get("netloc", "")
            ),
            "date": item.get("page_age", ""),
        })
    return results


def arxiv_search(topic: str, max_results: int, since: datetime.date) -> list[dict]:
    """Busca papers recientes sobre un topic en Arxiv, filtrando por fecha."""
    params = urllib.parse.urlencode({
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results * 3,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    url = f"http://export.arxiv.org/api/query?{params}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            xml_data = resp.read()
    except urllib.error.URLError as e:
        raise RuntimeError(str(e.reason))

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_data)
    papers = []
    for entry in root.findall("atom:entry", ns):
        published_raw = entry.findtext("atom:published", "", ns)
        if not published_raw:
            continue
        try:
            published = datetime.date.fromisoformat(published_raw[:10])
        except ValueError:
            continue
        if published < since:
            continue

        title = (entry.findtext("atom:title", "", ns) or "").strip().replace("\n", " ")
        url_ = entry.findtext("atom:id", "", ns) or ""
        authors = [
            a.findtext("atom:name", "", ns)
            for a in entry.findall("atom:author", ns)
        ]
        summary = (entry.findtext("atom:summary", "", ns) or "").strip().replace("\n", " ")
        papers.append({
            "title": title,
            "url": url_,
            "authors": [a for a in authors[:3] if a],
            "date": published_raw[:10],
            "abstract": summary[:400],
        })
        if len(papers) >= max_results:
            break
    return papers


def llamar_ia(prompt: str, api_key: str, model: str) -> str:
    """Llama a OpenCode Zen y devuelve el texto de respuesta."""
    payload = json.dumps({
        "model": model,
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://opencode.ai/zen/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "User-Agent": "cerebro-digest-semanal/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            respuesta = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
    except urllib.error.URLError as e:
        raise RuntimeError(str(e.reason))

    return respuesta["content"][0]["text"].strip()


def generar_resumen(
    carpeta: str,
    topics: list[str],
    noticias: list[dict],
    papers: list[dict],
    api_key: str,
    model: str,
) -> str:
    noticias_txt = "\n".join(
        f"- {n['title']} — {n['source']} ({n['date']})\n  {n['description']}"
        for n in noticias
    ) or "(sin noticias esta semana)"

    papers_txt = "\n".join(
        f"- {p['title']} — {', '.join(p['authors'])} ({p['date']})\n  {p['abstract']}"
        for p in papers
    ) or "(sin papers esta semana)"

    prompt = (
        f"Proyecto: {carpeta}\n"
        f"Topics de interés: {', '.join(topics)}\n\n"
        f"## Noticias y artículos de la semana\n{noticias_txt}\n\n"
        f"## Papers científicos recientes (Arxiv)\n{papers_txt}\n\n"
        "Genera el resumen ejecutivo en español (3-5 párrafos) sobre el estado del arte de esta semana."
    )
    return llamar_ia(prompt, api_key, model)


def generar_informe(
    carpeta: str,
    semana: str,
    fecha_generacion: str,
    noticias: list[dict],
    papers: list[dict],
    resumen: str,
) -> str:
    lineas = [
        f"# Digest Semanal — {carpeta} — Semana {semana}",
        "",
        f"> Generado el {fecha_generacion} | {len(noticias)} noticias · {len(papers)} papers",
        "",
        "## Resumen ejecutivo",
        "",
        resumen,
        "",
        "## Noticias y artículos",
        "",
    ]
    for n in noticias:
        meta = " · ".join(x for x in [n.get("source", ""), n.get("date", "")] if x)
        lineas.append(f"- [{n['title']}]({n['url']}) — {meta}")

    lineas += ["", "## Papers científicos (Arxiv)", ""]
    for p in papers:
        autores = ", ".join(p["authors"])
        lineas.append(f"- [{p['title']}]({p['url']}) — {autores} · {p['date']}")

    return "\n".join(lineas) + "\n"


def main() -> None:
    brave_api_key = os.environ.get("BRAVE_API_KEY")
    llm_api_key = os.environ.get("LLM_API_KEY")
    vault_path = os.environ.get("VAULT_PATH")

    if not brave_api_key:
        log.error("BRAVE_API_KEY no está definida")
        sys.exit(1)
    if not llm_api_key:
        log.error("LLM_API_KEY no está definida")
        sys.exit(1)
    if not vault_path:
        log.error("VAULT_PATH no está definida")
        sys.exit(1)

    digest_days = int(os.environ.get("DIGEST_DAYS", "7"))
    model = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")
    brave_results = int(os.environ.get("BRAVE_RESULTS_PER_TOPIC", "5"))
    arxiv_results = int(os.environ.get("ARXIV_RESULTS_PER_TOPIC", "5"))

    hoy = datetime.date.today()
    iso_year, iso_week, _ = hoy.isocalendar()
    semana = f"{iso_year}-W{iso_week:02d}"
    fecha_inicio = hoy - datetime.timedelta(days=digest_days)

    index_path = Path(vault_path) / "proyectos" / "INDEX.md"
    try:
        index_md = index_path.read_text(encoding="utf-8")
    except OSError as e:
        log.error("No se pudo leer %s: %s", index_path, e)
        sys.exit(1)

    proyectos = parse_proyectos(index_md)
    if not proyectos:
        log.error("No se encontraron proyectos activos con topics en INDEX.md")
        sys.exit(1)

    log.info("Inicio digest %s | %d proyectos encontrados", semana, len(proyectos))

    proyectos_ok = 0
    for proyecto in proyectos:
        carpeta = proyecto["carpeta"]
        topics = proyecto["topics"]

        informe_dir = Path(vault_path) / "proyectos" / carpeta / "informes"
        informe_path = informe_dir / f"{semana}.md"

        if informe_path.exists():
            log.warning("Informe ya existe para '%s' (%s) — omitiendo", carpeta, semana)
            proyectos_ok += 1
            continue

        log.info("Procesando '%s' | topics: %s", carpeta, ", ".join(topics))

        todas_noticias: list[dict] = []
        todos_papers: list[dict] = []
        topics_ok = 0

        for topic in topics:
            try:
                noticias = brave_search(topic, brave_api_key, brave_results)
                todas_noticias.extend(noticias)
                log.info("  Brave '%s': %d resultados", topic, len(noticias))
                topics_ok += 1
            except RuntimeError as e:
                log.warning("  Brave error en topic '%s' de '%s': %s", topic, carpeta, e)

            try:
                papers = arxiv_search(topic, arxiv_results, fecha_inicio)
                todos_papers.extend(papers)
                log.info("  Arxiv '%s': %d papers", topic, len(papers))
            except RuntimeError as e:
                log.warning("  Arxiv error en topic '%s' de '%s': %s", topic, carpeta, e)

        if topics_ok == 0:
            log.error("Todos los topics fallaron para '%s' — omitiendo proyecto", carpeta)
            continue

        seen: set[str] = set()
        noticias_unicas = [n for n in todas_noticias if not (n["url"] in seen or seen.add(n["url"]))]  # type: ignore[func-returns-value]

        seen_arxiv: set[str] = set()
        papers_unicos = [p for p in todos_papers if not (p["url"] in seen_arxiv or seen_arxiv.add(p["url"]))]  # type: ignore[func-returns-value]

        log.info("  Total: %d noticias, %d papers únicos", len(noticias_unicas), len(papers_unicos))

        try:
            resumen = generar_resumen(
                carpeta, topics, noticias_unicas, papers_unicos,
                llm_api_key, model,
            )
        except RuntimeError as e:
            log.error("Error en llamada a IA para '%s': %s", carpeta, e)
            continue

        informe_dir.mkdir(parents=True, exist_ok=True)
        contenido = generar_informe(
            carpeta, semana, hoy.isoformat(),
            noticias_unicas, papers_unicos, resumen,
        )
        informe_path.write_text(contenido, encoding="utf-8")
        log.info("Informe guardado: %s", informe_path)
        proyectos_ok += 1

    if proyectos_ok == 0:
        log.error("Ningún proyecto procesado con éxito")
        sys.exit(1)

    log.info("Digest completado: %d/%d proyectos procesados", proyectos_ok, len(proyectos))


if __name__ == "__main__":
    main()
