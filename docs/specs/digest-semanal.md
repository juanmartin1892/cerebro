# Spec: digest-semanal

## Propósito

Genera semanalmente un informe por cada proyecto activo en Vault, recopilando noticias recientes (Brave Search) y papers científicos (Arxiv) sobre los topics del proyecto, y sintetizando un resumen ejecutivo con Claude.

## Cron schedule

```cron
# m h dom mon dow command
0 7 * * 1  /path/to/scripts/digest-semanal.py >> /var/log/cerebro/digest-semanal.log 2>&1
```

Ejecuta cada lunes a las 7:00 AM, cubriendo los 7 días anteriores.

## Entradas

### Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `BRAVE_API_KEY` | Clave de la Brave Search API | `BSAabc123...` |
| `LLM_API_KEY` | Clave de la API de OpenCode Zen | `...` |
| `VAULT_PATH` | Ruta absoluta a la raíz del vault | `/home/juan/vault` |

### Variables de entorno opcionales

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `DIGEST_DAYS` | Días hacia atrás a cubrir | `7` |
| `LLM_MODEL` | Modelo a usar | `claude-sonnet-4-6` |
| `BRAVE_RESULTS_PER_TOPIC` | Resultados de Brave por topic | `5` |
| `ARXIV_RESULTS_PER_TOPIC` | Papers de Arxiv por topic | `5` |

### Archivos de entrada

- `{VAULT_PATH}/proyectos/INDEX.md` — fuente de proyectos activos y sus topics

**Formato esperado de la tabla de activos en INDEX.md:**

```markdown
| Proyecto | Descripción | Topics | Última actualización |
|----------|-------------|--------|---------------------|
| [[carpeta/README\|Nombre]] | Descripción | topic1, topic2, topic3 | YYYY-MM-DD |
```

El script extrae el nombre de carpeta del enlace Obsidian (`[[carpeta/README|...]]`) y los topics de la columna correspondiente.

## Salidas

### Stdout / log

- Inicio de ejecución con fecha y número de proyectos encontrados
- Por cada proyecto: topics encontrados, número de resultados Brave y Arxiv obtenidos
- Ruta del informe generado al terminar cada proyecto
- En caso de error por proyecto: mensaje con el proyecto afectado y causa, continuando con los demás

### Archivos generados

- `{VAULT_PATH}/proyectos/{nombre}/informes/YYYY-WXX.md` — un informe por proyecto por semana

**Formato del informe:**

```markdown
# Digest Semanal — {Nombre Proyecto} — Semana {YYYY-WXX}

> Generado el {fecha} | {n} noticias · {m} papers

## Resumen ejecutivo

{3-5 párrafos en español sintetizando el estado del arte de la semana,
 generados por Claude a partir de los títulos, snippets y abstracts recopilados}

## Noticias y artículos

- [Título](URL) — Fuente · Fecha

## Papers científicos (Arxiv)

- [Título](URL) — Autores · Fecha
```

### Efectos secundarios

- Llamadas a Brave Search API (una por topic por proyecto)
- Llamadas a Arxiv API (una por topic por proyecto)
- Una llamada a Claude API por proyecto para generar el resumen ejecutivo
- Creación de la carpeta `informes/` si no existe

## Dependencias Python

Solo stdlib + módulos disponibles en el VPS. Sin dependencias externas.

## Comportamiento ante errores

- **Variable de entorno faltante**: salir inmediatamente con código 1 y mensaje claro
- **Error de red en Brave o Arxiv para un topic**: loguear warning, continuar con el resto de topics del proyecto
- **Error de red en Brave o Arxiv para todos los topics de un proyecto**: loguear error, saltar ese proyecto, continuar con los demás
- **Error en llamada a Claude**: loguear error con el proyecto afectado, saltar ese proyecto
- **Informe ya existe** (`YYYY-WXX.md`): loguear warning y saltar (idempotente — no sobreescribir)
- **Exit code**: `0` si al menos un proyecto se procesó con éxito; `1` si todos fallaron o no se encontraron proyectos activos con topics

## Notas de implementación

- Parsear INDEX.md con regex sobre la tabla Markdown; no asumir librerías de parsing MD
- El nombre de carpeta se extrae del enlace Obsidian: `[[carpeta/README|...]]` → `carpeta`
- La semana ISO se obtiene con `datetime.date.today().isocalendar()` → formato `YYYY-WXX` (e.g. `2026-W16`)
- Brave Search API endpoint: `https://api.search.brave.com/res/v1/web/search` con header `X-Subscription-Token`; añadir parámetro `freshness=pw` para resultados de la última semana
- Arxiv API: `http://export.arxiv.org/api/query` con parámetros `search_query`, `start=0`, `max_results`, `sortBy=submittedDate`, `sortOrder=descending`; filtrar por fecha de submission >= fecha inicio de ventana
- Prompt a Claude: incluir todos los títulos + snippets/abstracts recopilados; pedir resumen ejecutivo en español de 3-5 párrafos sobre el estado del arte de la semana
- Llamadas a la IA via `urllib.request` directamente al endpoint `https://opencode.ai/zen/v1/messages` (mismo patrón que `menu-semanal`), sin SDK externo
