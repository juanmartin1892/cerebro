# Spec: sincronizar-vault-recetas

## Propósito

Mantiene sincronizados los índices y fichas de ingredientes y técnicas del vault de recetas. Se ejecuta diariamente y procesa todos los archivos `.md` de `/vault/recetas/` para detectar ingredientes y técnicas nuevas, crear sus fichas stub si no existen, y reconstruir los ficheros `INDEX.md` de recetas, ingredientes y técnicas.

Sustituye el flujo manual en el que el modelo de Open WebUI creaba todos los archivos en la misma conversación. Con este script, Open WebUI solo necesita crear el archivo de receta.

## Cron schedule

```cron
# Diariamente a las 03:00
0 3 * * * /opt/cerebro/scripts/sincronizar-vault-recetas.py >> /var/log/cerebro/sincronizar-vault-recetas.log 2>&1
```

## Entradas

### Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `VAULT_RECETAS_PATH` | Ruta absoluta al directorio de recetas en el vault | `/home/juan/vault/recetas` |

### Variables de entorno opcionales

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `DRY_RUN` | Si `1`, imprime cambios sin escribir nada | `0` |

### Archivos de entrada

- `$VAULT_RECETAS_PATH/*.md` — archivos de receta creados por Open WebUI
- `$VAULT_RECETAS_PATH/ingredientes/INDEX.md` — índice actual de ingredientes (puede no existir)
- `$VAULT_RECETAS_PATH/tecnicas/INDEX.md` — índice actual de técnicas (puede no existir)

## Salidas

### Stdout / log

Ejecución normal:
```
2026-04-18 03:00:01 [INFO] Iniciando sincronización — 25 recetas encontradas
2026-04-18 03:00:01 [INFO] Receta nueva detectada: espinacas-con-garbanzos.md
2026-04-18 03:00:01 [INFO] Ingrediente nuevo: Espinacas → creado stub
2026-04-18 03:00:01 [INFO] Ingrediente nuevo: Garbanzos → creado stub
2026-04-18 03:00:02 [INFO] INDEX.md de recetas actualizado (25 entradas)
2026-04-18 03:00:02 [INFO] INDEX.md de ingredientes actualizado (46 entradas)
2026-04-18 03:00:02 [INFO] INDEX.md de técnicas sin cambios
2026-04-18 03:00:02 [INFO] Sincronización completada en 1.2s
```

Sin cambios:
```
2026-04-18 03:00:01 [INFO] Iniciando sincronización — 25 recetas encontradas
2026-04-18 03:00:01 [INFO] Sin cambios detectados
```

Error:
```
2026-04-18 03:00:01 [ERROR] VAULT_RECETAS_PATH no está definida
```

### Archivos generados / modificados

- `$VAULT_RECETAS_PATH/INDEX.md` — reconstruido desde cero en cada ejecución
- `$VAULT_RECETAS_PATH/ingredientes/INDEX.md` — reconstruido desde cero
- `$VAULT_RECETAS_PATH/tecnicas/INDEX.md` — reconstruido desde cero
- `$VAULT_RECETAS_PATH/ingredientes/<Nombre>.md` — stub creado si no existe
- `$VAULT_RECETAS_PATH/tecnicas/Técnica <Nombre>.md` — stub creado si no existe

Los stubs nunca sobreescriben fichas existentes.

### Efectos secundarios

- Escribe archivos directamente en el vault (sincronizado a otros dispositivos via Syncthing)

## Lógica de procesamiento

### Extracción de datos de cada receta

El script parsea cada `.md` de recetas buscando:

1. **Metadatos**: líneas `- Categoría:`, `- Dificultad:`, `- Tiempo:`, `- Raciones:`, `- Temporada:`
2. **Ingredientes**: todas las ocurrencias de `[[Nombre]]` dentro de la sección `## Ingredientes`
3. **Técnicas**: todas las ocurrencias de `[[Nombre]]` dentro de la sección `## Técnicas`
4. **Ingredientes principales**: los primeros 6 ingredientes únicos encontrados

### Reconstrucción de INDEX.md de recetas

Se regenera completamente en cada ejecución a partir de los datos parseados:
- Entradas en orden alfabético por nombre de archivo
- Sección "Búsqueda por Categorías" al final, agrupando por categoría

### Creación de stubs

Si `ingredientes/<Nombre>.md` no existe, se crea con:
```markdown
# <Nombre>

## Descripción
Pendiente de documentar.

## Recetas donde aparece
- [[<Nombre Receta>]] — ingrediente

## Enlaces
```

Ídem para técnicas en `tecnicas/Técnica <Nombre>.md`.

### Archivos ignorados

- `INDEX.md` en cualquier subdirectorio
- Archivos cuyo nombre empiece por `_`
- Archivos en subdirectorios (`ingredientes/`, `tecnicas/`)

## Dependencias Python

```
# No requiere dependencias externas — solo stdlib
```

## Comportamiento ante errores

- **`VAULT_RECETAS_PATH` no definida**: salir con código 1 y mensaje claro
- **Directorio no existe**: salir con código 1
- **Receta con formato incorrecto** (metadatos no parseables): loguear warning y continuar con la siguiente — no abortar
- **Error de escritura en un archivo**: loguear error y continuar con el resto
- **`DRY_RUN=1`**: no escribir nada, solo loguear qué se haría

## Notas de implementación

- El script es **completamente idempotente** — ejecutarlo N veces produce el mismo resultado
- Los INDEX se reconstruyen desde cero en cada ejecución; no se hacen edits parciales
- Los stubs de ingredientes y técnicas **nunca sobreescriben** archivos existentes (check `os.path.exists` antes de crear)
- El nombre del ingrediente/técnica se extrae tal cual del wikilink: `[[Aceite de Oliva]]` → `Aceite de Oliva.md`
- El nombre de la receta para el INDEX se extrae del encabezado `# Título` del archivo, no del nombre de fichero
- Compatibilidad: el vault está en la ruta local del VPS donde Syncthing mantiene la copia sincronizada; acceso directo al filesystem, sin MCP
