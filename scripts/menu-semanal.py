#!/usr/bin/env python3
"""
menu-semanal.py — Genera un menú semanal orientativo cada domingo usando recetas del vault.

Lee las recetas disponibles, productos de temporada y recomendaciones nutricionales,
llama a la IA (OpenCode Zen) una sola vez para generar el menú y dos recetas nuevas,
y escribe los resultados como notas Obsidian en el vault.

Cron: 0 9 * * 0  /path/to/scripts/menu-semanal.py >> /var/log/cerebro/menu-semanal.log 2>&1
"""

import json
import logging
import os
import re
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

import urllib.request
import urllib.error

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def slugify(texto: str) -> str:
    """Convierte un texto a kebab-case ASCII para nombres de archivo."""
    normalizado = unicodedata.normalize("NFKD", texto)
    ascii_ = normalizado.encode("ascii", "ignore").decode("ascii")
    lower = ascii_.lower()
    limpio = re.sub(r"[^\w\s-]", "", lower)
    return re.sub(r"[\s_]+", "-", limpio).strip("-")


def leer_archivo(ruta: Path) -> str:
    if not ruta.exists():
        log.error("Archivo no encontrado: %s", ruta)
        sys.exit(1)
    return ruta.read_text(encoding="utf-8")


def extraer_recetas_del_index(index_md: str) -> list[dict]:
    """Extrae nombre, categoría y temporada de cada receta del INDEX."""
    recetas = []
    patron = re.compile(
        r"^## (.+?)\n"
        r".*?- \*\*Archivo\*\*: `(.+?)`\n"
        r".*?- \*\*Categoría\*\*: (.+?)\n"
        r".*?- \*\*Temporada\*\*: (.+?)$",
        re.MULTILINE | re.DOTALL,
    )
    for m in patron.finditer(index_md):
        nombre, archivo, categoria, temporada = m.group(1), m.group(2), m.group(3), m.group(4)
        recetas.append({
            "nombre": nombre.strip(),
            "archivo": archivo.strip(),
            "categoria": categoria.strip(),
            "temporada": temporada.strip(),
        })
    return recetas


def extraer_temporada_mes(calendario_md: str, mes_nombre: str) -> str:
    """Extrae la línea de frutas y verduras del mes actual."""
    patron = re.compile(
        rf"## MES: {re.escape(mes_nombre)}\nFRUTAS: ([^\n]+)\nVERDURAS: ([^\n]+)",
        re.IGNORECASE,
    )
    m = patron.search(calendario_md)
    if not m:
        log.warning("No se encontró el mes '%s' en el calendario", mes_nombre)
        return ""
    return f"Frutas: {m.group(1)}\nVerduras: {m.group(2)}"


def extraer_notas_nutricionales(recomendaciones_md: str) -> str:
    """Extrae solo la sección 'Notas de Uso para Scripts' del archivo nutricional."""
    patron = re.compile(r"## Notas de Uso para Scripts\n(.*?)(?=\n---|\Z)", re.DOTALL)
    m = patron.search(recomendaciones_md)
    if not m:
        # Fallback: usar la sección de Recomendaciones Generales OMS
        patron2 = re.compile(r"## Recomendaciones Generales OMS\n(.*?)(?=\n---|\Z)", re.DOTALL)
        m2 = patron2.search(recomendaciones_md)
        return m2.group(1).strip() if m2 else ""
    return m.group(1).strip()


def construir_prompt(
    recetas: list[dict],
    temporada: str,
    notas_nutri: str,
    plantilla_receta: str,
    lunes: date,
) -> str:
    recetas_txt = "\n".join(
        f"- {r['nombre']} (categoría: {r['categoria']}, temporada: {r['temporada']})"
        for r in recetas
    )
    archivos_existentes = [r["archivo"].lower() for r in recetas]

    return f"""Eres un asistente de planificación de menús semanales.
Genera un menú para la semana que empieza el {lunes.strftime('%d/%m/%Y')}.

## Recetas disponibles en el vault
{recetas_txt}

## Productos de temporada ({MESES_ES[lunes.month - 1]})
{temporada}

## Directrices nutricionales
{notas_nutri}

## Instrucciones
1. Asigna un plato de almuerzo y uno de cena a cada día (Lunes a Domingo). Los platos DEBEN ser de la lista de recetas disponibles.
2. Para cada día añade una recomendación breve (1 frase) para el resto del día (desayuno/meriendas).
3. Propón exactamente 2 recetas nuevas que complementen los huecos de temporada o nutricionales. Escríbelas completas siguiendo esta plantilla:

{plantilla_receta}

4. Los archivos de las recetas nuevas no deben coincidir (case-insensitive) con ninguno de estos archivos existentes:
{json.dumps(archivos_existentes)}

## Formato de respuesta
Responde ÚNICAMENTE con JSON válido, sin texto adicional ni bloques de código markdown. Esquema exacto:

{{
  "recomendaciones_semana": "string con 1-3 observaciones nutricionales o de temporada para esta semana",
  "dias": [
    {{
      "dia": "Lunes",
      "almuerzo": {{"nombre": "Nombre exacto de la receta", "archivo": "nombre-archivo-sin-extension"}},
      "cena": {{"nombre": "Nombre exacto de la receta", "archivo": "nombre-archivo-sin-extension"}},
      "resto_dia": "Recomendación breve para desayuno/meriendas"
    }}
  ],
  "recetas_nuevas": [
    {{
      "nombre": "Nombre de la receta nueva",
      "archivo": "nombre-kebab-case",
      "contenido_md": "Contenido completo de la nota en Markdown según la plantilla"
    }}
  ]
}}

El array "dias" debe tener exactamente 7 elementos (Lunes a Domingo).
El array "recetas_nuevas" debe tener exactamente 2 elementos.
"""


def llamar_ia(prompt: str, api_key: str, model: str) -> dict:
    """Llama a OpenCode Zen (endpoint /messages) y devuelve el JSON parseado."""
    payload = json.dumps({
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://opencode.ai/zen/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "User-Agent": "cerebro-menu-semanal/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            respuesta = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode("utf-8", errors="replace")
        log.error("Error HTTP %s de la API: %s", e.code, cuerpo)
        sys.exit(1)
    except urllib.error.URLError as e:
        log.error("Error de conexión con la API: %s", e.reason)
        sys.exit(1)

    contenido = respuesta["content"][0]["text"].strip()

    # Limpiar posibles bloques de código markdown que la IA incluya igualmente
    if contenido.startswith("```"):
        contenido = re.sub(r"^```[a-z]*\n?", "", contenido)
        contenido = re.sub(r"\n?```$", "", contenido)

    try:
        return json.loads(contenido)
    except json.JSONDecodeError as e:
        log.error("JSON malformado en respuesta de la IA: %s", e)
        log.error("Respuesta raw: %s", contenido)
        sys.exit(1)


def generar_nota_menu(datos: dict, lunes: date) -> str:
    """Construye el contenido Markdown de la nota de menú."""
    fecha_str = lunes.strftime("%Y-%m-%d")
    dia_num = lunes.day
    mes_nombre = MESES_ES[lunes.month - 1]
    año = lunes.year
    hoy = date.today().strftime("%Y-%m-%d")

    lineas = [
        "---",
        "tags: [menu, semanal]",
        f"semana: {fecha_str}",
        f"created: {hoy}",
        "---",
        "",
        f"# Menú semana del {dia_num} de {mes_nombre} de {año}",
        "",
        "## Recomendaciones generales de la semana",
        datos["recomendaciones_semana"],
        "",
    ]

    for dia_datos in datos["dias"]:
        dia = dia_datos["dia"]
        almuerzo = dia_datos["almuerzo"]
        cena = dia_datos["cena"]
        resto = dia_datos["resto_dia"]
        lineas += [
            f"## {dia}",
            f"**Almuerzo:** {almuerzo['nombre']} → `[[{almuerzo['archivo']}]]`",
            f"**Cena:** {cena['nombre']} → `[[{cena['archivo']}]]`",
            f"**Resto del día:** {resto}",
            "",
        ]

    lineas += ["## Recetas nuevas esta semana"]
    for receta in datos["recetas_nuevas"]:
        lineas.append(f"- `[[{receta['archivo']}]]`")

    return "\n".join(lineas) + "\n"


def entrada_index(receta: dict) -> str:
    """Genera la entrada de INDEX.md para una receta nueva."""
    return (
        f"\n## {receta['nombre']}\n"
        f"- **Archivo**: `{receta['archivo']}.md`\n"
        f"- **Categoría**: Pendiente\n"
        f"- **Dificultad**: Pendiente\n"
        f"- **Tiempo**: Pendiente\n"
        f"- **Raciones**: Pendiente\n"
        f"- **Ingredientes principales**: Pendiente\n"
        f"- **Técnicas**: Pendiente\n"
        f"- **Temporada**: Pendiente\n"
    )


def actualizar_index(index_path: Path, recetas_nuevas: list[dict]) -> None:
    """Añade las recetas nuevas al INDEX.md antes de la línea '---' de cierre."""
    contenido = index_path.read_text(encoding="utf-8")
    entradas = "".join(entrada_index(r) for r in recetas_nuevas)

    # Insertar antes del último bloque '---\n' al final del archivo
    if "\n---\n" in contenido:
        pos = contenido.rfind("\n---\n")
        nuevo = contenido[:pos] + entradas + contenido[pos:]
    else:
        nuevo = contenido.rstrip() + "\n" + entradas

    index_path.write_text(nuevo, encoding="utf-8")


def main() -> None:
    api_key = os.environ.get("LLM_API_KEY")
    vault_path_str = os.environ.get("VAULT_PATH")
    model = os.environ.get("LLM_MODEL", "claude-haiku-4-5")

    if not api_key:
        log.error("LLM_API_KEY no está definida")
        sys.exit(1)
    if not vault_path_str:
        log.error("VAULT_PATH no está definida")
        sys.exit(1)

    vault = Path(vault_path_str)

    # Calcular el lunes objetivo: si hoy es domingo, es el lunes de mañana;
    # si no, es el lunes de la semana en curso.
    hoy = date.today()
    if hoy.weekday() == 6:  # domingo
        lunes = hoy + timedelta(days=1)
    else:
        lunes = hoy - timedelta(days=hoy.weekday())

    # Comprobar idempotencia
    menu_dir = vault / "inbox" / "menus"
    menu_path = menu_dir / f"menu-{lunes.strftime('%Y-%m-%d')}.md"
    if menu_path.exists():
        log.info("El menú de esta semana ya existe: %s — nada que hacer.", menu_path)
        sys.exit(0)

    # Leer archivos de entrada
    index_path = vault / "recetas" / "INDEX.md"
    index_md = leer_archivo(index_path)
    calendario_md = leer_archivo(vault / "recetas" / "calendario-productos-temporada.md")
    recomendaciones_md = leer_archivo(vault / "recetas" / "recomendaciones-nutricionales.md")
    plantilla_receta = leer_archivo(vault / "_templates" / "receta.md")

    # Construir contexto compacto
    recetas = extraer_recetas_del_index(index_md)
    if not recetas:
        log.error("No se encontraron recetas en INDEX.md — revisa el formato del archivo.")
        sys.exit(1)
    log.info("Recetas disponibles: %d", len(recetas))

    mes_nombre = MESES_ES[lunes.month - 1].capitalize()
    temporada = extraer_temporada_mes(calendario_md, mes_nombre)
    notas_nutri = extraer_notas_nutricionales(recomendaciones_md)

    # Llamada única a la IA
    log.info("Llamando a la IA (modelo: %s)...", model)
    prompt = construir_prompt(recetas, temporada, notas_nutri, plantilla_receta, lunes)
    datos = llamar_ia(prompt, api_key, model)

    # Validar estructura mínima de la respuesta
    if "dias" not in datos or len(datos["dias"]) != 7:
        log.error("La respuesta de la IA no contiene exactamente 7 días.")
        sys.exit(1)
    if "recetas_nuevas" not in datos or not isinstance(datos["recetas_nuevas"], list):
        log.error("La respuesta de la IA no contiene el campo 'recetas_nuevas'.")
        sys.exit(1)

    # Filtrar recetas nuevas que dupliquen archivos existentes
    archivos_existentes = {r["archivo"].lower() for r in recetas}
    recetas_nuevas_filtradas = []
    for r in datos["recetas_nuevas"]:
        archivo_slug = slugify(r.get("archivo", r["nombre"]))
        if archivo_slug in archivos_existentes:
            log.warning("Receta nueva '%s' ya existe en el INDEX — descartada.", r["nombre"])
        else:
            r["archivo"] = archivo_slug
            recetas_nuevas_filtradas.append(r)

    datos["recetas_nuevas"] = recetas_nuevas_filtradas

    # Escribir menú
    os.makedirs(menu_dir, exist_ok=True)
    nota_menu = generar_nota_menu(datos, lunes)
    menu_path.write_text(nota_menu, encoding="utf-8")
    log.info("Menú guardado en: %s", menu_path)

    # Escribir recetas nuevas
    recetas_dir = vault / "recetas"
    for receta in datos["recetas_nuevas"]:
        ruta_receta = recetas_dir / f"{receta['archivo']}.md"
        if ruta_receta.exists():
            log.warning("El archivo de receta ya existe: %s — no se sobreescribe.", ruta_receta)
            continue
        ruta_receta.write_text(receta["contenido_md"], encoding="utf-8")
        log.info("Receta nueva: %s", ruta_receta)

    # Actualizar INDEX.md
    if datos["recetas_nuevas"]:
        actualizar_index(index_path, datos["recetas_nuevas"])
        log.info("INDEX.md actualizado con %d receta(s) nueva(s).", len(datos["recetas_nuevas"]))

    log.info("Menú semanal generado correctamente.")


if __name__ == "__main__":
    main()
