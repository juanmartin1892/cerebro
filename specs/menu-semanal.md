# Spec: menu-semanal

## Propósito

Genera cada domingo un menú semanal orientativo con almuerzo y cena para 7 días, usando recetas del vault y proponiendo dos recetas nuevas. El menú se guarda como nota Obsidian en `vault/inbox/menus/` y las recetas nuevas se añaden a `vault/recetas/` y al `INDEX.md`.

## Cron schedule

```cron
# Cada domingo a las 9:00
0 9 * * 0  /path/to/scripts/menu-semanal.py >> /var/log/cerebro/menu-semanal.log 2>&1
```

## Entradas

### Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `LLM_API_KEY` | API key de OpenCode Zen | `zen-abc123` |
| `VAULT_PATH` | Ruta absoluta al vault de Obsidian | `/home/user/vault` |

### Variables de entorno opcionales

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `LLM_MODEL` | Modelo a usar en OpenCode Zen | `claude-haiku-4-5` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

### Archivos de entrada (leídos en cada ejecución)

- `$VAULT_PATH/recetas/INDEX.md` — lista de recetas disponibles
- `$VAULT_PATH/recetas/calendario-productos-temporada.md` — productos de temporada por mes
- `$VAULT_PATH/recetas/recomendaciones-nutricionales.md` — directrices nutricionales
- `$VAULT_PATH/_templates/receta.md` — plantilla para nuevas recetas

## Salidas

### Archivos generados

- `$VAULT_PATH/inbox/menus/menu-YYYY-MM-DD.md` — nota Obsidian con el menú de la semana (fecha = lunes de esa semana)
- `$VAULT_PATH/recetas/[nombre-receta-nueva-1].md` — primera receta nueva
- `$VAULT_PATH/recetas/[nombre-receta-nueva-2].md` — segunda receta nueva

### Modificaciones

- `$VAULT_PATH/recetas/INDEX.md` — se añaden al final las dos entradas nuevas con el formato establecido

### Formato del menú (`menu-YYYY-MM-DD.md`)

```markdown
---
tags: [menu, semanal]
semana: YYYY-MM-DD
created: YYYY-MM-DD
---

# Menú semana del DD de [mes] de YYYY

## Recomendaciones generales de la semana
- [1-3 líneas con contexto nutricional o de temporada]

## Lunes
**Almuerzo:** [Nombre receta] → `[[nombre-archivo]]`
**Cena:** [Nombre receta] → `[[nombre-archivo]]`
**Resto del día:** [Recomendación desayuno/merienda]

## Martes
...

## Recetas nuevas esta semana
- `[[nombre-receta-nueva-1]]`
- `[[nombre-receta-nueva-2]]`
```

### Stdout / log

- Una línea por cada archivo escrito: `Menú guardado en: ...`, `Receta nueva: ...`
- En caso de error: descripción del problema y exit 1

## Dependencias Python

Solo stdlib — no requiere instalar paquetes externos. Usa `urllib.request` para la llamada HTTP al endpoint `/messages` de OpenCode Zen.

## Comportamiento ante errores

- **`LLM_API_KEY` o `VAULT_PATH` no definidas**: salir con código 1 y mensaje claro antes de hacer ninguna llamada.
- **Archivo de entrada no encontrado** (`INDEX.md`, calendario, etc.): salir con código 1 indicando qué archivo falta.
- **Error HTTP de la API** (4xx/5xx): loggear el código y cuerpo de respuesta, salir con código 1. No reintentar (el cron volverá a ejecutar el siguiente domingo).
- **JSON malformado en respuesta de la IA**: loggear la respuesta raw, salir con código 1.
- **Menú de la semana ya existe** (`menu-YYYY-MM-DD.md` ya presente): loggear aviso y salir con código 0 sin sobreescribir (idempotencia).

## Diseño de la llamada a la IA

El script hace **una sola llamada** a la API con un contexto compacto construido así:

1. **Recetas disponibles**: extraer de `INDEX.md` solo nombre, categoría y temporada de cada receta (no los ingredientes completos).
2. **Temporada actual**: extraer del calendario solo la línea del mes en curso con regex (`## MES: [nombre]\nFRUTAS: ...\nVERDURAS: ...`).
3. **Directrices nutricionales**: usar únicamente la sección `## Notas de Uso para Scripts` del archivo de recomendaciones (ya contiene las reglas accionables resumidas).
4. **Plantilla de receta**: pasar el contenido de `_templates/receta.md` tal cual (es corta).

El prompt pide una respuesta en **JSON estructurado** con este esquema:

```json
{
  "recomendaciones_semana": "string",
  "dias": [
    {
      "dia": "Lunes",
      "almuerzo": {"nombre": "...", "archivo": "..."},
      "cena":     {"nombre": "...", "archivo": "..."},
      "resto_dia": "string"
    }
  ],
  "recetas_nuevas": [
    {
      "nombre": "string",
      "archivo": "nombre-kebab-case.md",
      "contenido_md": "string (nota completa según plantilla)"
    }
  ]
}
```

Este diseño evita múltiples llamadas y mantiene el contexto mínimo necesario.

## Notas de implementación

- Usar `anthropic.Anthropic(api_key=..., base_url="https://opencode.ai/zen/v1")` para apuntar a OpenCode Zen.
- El directorio `$VAULT_PATH/inbox/menus/` debe crearse si no existe (`os.makedirs(..., exist_ok=True)`).
- El nombre del archivo del menú usa la fecha del **lunes** de la semana en curso (`date.today() - timedelta(days=date.today().weekday())`).
- Las entradas nuevas en `INDEX.md` se añaden antes de la línea `---` de cierre (o al final si no existe).
- Los nombres de archivo de recetas nuevas deben ser kebab-case sin caracteres especiales (`unicodedata.normalize` + regex).
- Si la IA propone como receta nueva una que ya existe en el INDEX, descartar y dejar solo las que sean genuinamente nuevas (comparación case-insensitive por nombre de archivo).
- No incluir en el contexto enviado a la IA las instrucciones internas del vault ni rutas de sistema.
