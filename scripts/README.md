# Scripts de automatización — cerebro

Scripts de automatización del sistema. Se ejecutan via cron en el servidor principal.

## Estructura

```
scripts/
└── README.md   (este archivo)
```

## Añadir un nuevo script

1. Crear el script en esta carpeta
2. Documentarlo aquí (nombre, qué hace, frecuencia de ejecución)
3. Añadir la entrada al crontab del servidor: `crontab -e`

## Configuración de cron

Los scripts se ejecutan en el servidor principal. Plantilla para crontab:

```cron
# m h dom mon dow command
0 * * * *  /path/to/scripts/nombre-script.py >> /var/log/cerebro/nombre-script.log 2>&1
```

## Variables de entorno

Los scripts que necesiten credenciales las leen de variables de entorno o de un archivo `.env` local (nunca subido a git).

---

## Scripts disponibles

### `menu-semanal/`

Genera cada domingo un menú semanal orientativo (almuerzo + cena para 7 días) usando las recetas disponibles en el vault. Propone dos recetas nuevas por ejecución, las escribe como notas Obsidian en `vault/recetas/` y actualiza `INDEX.md`. El menú se guarda en `vault/inbox/menus/menu-YYYY-MM-DD.md`.

Accede al vault via el MCP server (SSE). Se ejecuta como contenedor Docker.

**Variables de entorno requeridas:** `LLM_API_KEY`, `MCP_VAULT_URL`
**Variables opcionales:** `MCP_VAULT_ROOT` (default: `/vault`), `LLM_MODEL` (default: `claude-haiku-4-5`), `LOG_LEVEL`

```cron
0 9 * * 0  docker run --rm --network host --env-file /path/to/infra/scripts/.env cerebro/menu-semanal >> /var/log/cerebro/menu-semanal.log 2>&1
```

### `digest-semanal.py`

Genera cada lunes un informe semanal por cada proyecto activo en el vault. Para cada proyecto lee los topics del `proyectos/INDEX.md`, consulta Brave Search (noticias) y Arxiv (papers) de los últimos 7 días, y usa Claude para sintetizar un resumen ejecutivo en español. Guarda el informe en `proyectos/{nombre}/informes/YYYY-WXX.md`.

**Variables de entorno requeridas:** `BRAVE_API_KEY`, `LLM_API_KEY`, `VAULT_PATH`
**Variables opcionales:** `DIGEST_DAYS` (default: `7`), `LLM_MODEL` (default: `claude-sonnet-4-6`), `BRAVE_RESULTS_PER_TOPIC` (default: `5`), `ARXIV_RESULTS_PER_TOPIC` (default: `5`), `LOG_LEVEL`

```cron
0 7 * * 1  /path/to/scripts/digest-semanal.py >> /var/log/cerebro/digest-semanal.log 2>&1
```
