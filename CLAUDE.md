# Cerebro — Instrucciones para Claude Code

## Proyecto

Sistema de automatización personal. Scripts Python/Bash que corren via cron en un VPS privado accesible por Tailscale. Reemplazan workflows anteriores.

## Regla fundamental

**Siempre spec antes de código.** Antes de implementar cualquier script, debe existir su spec en `specs/[nombre].md`. Si no existe, ejecutar `/escribir-spec` primero.

## Estructura del repositorio

| Carpeta | Propósito |
|---------|-----------|
| `specs/` | Especificaciones de cada script. Una por script. |
| `scripts/` | Implementaciones. El nombre del archivo debe coincidir con el de su spec. |
| `profiles/behaviors/` | Perfiles de comportamiento importados según la tarea. |
| `profiles/envs/` | Plantillas de variables de entorno por entorno. |
| `.claude/commands/` | Comandos slash disponibles en este proyecto. |

## Perfiles de comportamiento

@profiles/behaviors/new-script.md
@profiles/behaviors/debug.md
@profiles/behaviors/refactor.md

## Convenciones de código

- Python 3.11+
- Una función `main()` por script, con `if __name__ == "__main__": main()`
- Logging a stdout con `logging` estándar (nivel INFO por defecto)
- Credenciales y configuración **solo** via `os.environ` — nunca hardcodeadas
- Cada script debe poder ejecutarse sin argumentos (toda config via env vars)
- Al final de cada script, un comentario con la línea de cron sugerida

## Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `/escribir-spec [descripción]` | Genera una spec en `specs/` desde una descripción |
| `/crear-script [nombre]` | Implementa el script a partir de `specs/[nombre].md` |
| `/revisar-script [nombre]` | Revisa el script contra su spec |
| `/lint` | Ejecuta flake8 + black sobre `scripts/` |
| `/worktree-deliver` | Empaqueta cambios como PR con commit convencional |

## Entornos

Los scripts corren en dos entornos. Ver `profiles/envs/` para las variables necesarias en cada uno.

- **vps**: Servidor principal (Ubuntu 24.04, red Tailscale)
- **local**: Estación de trabajo para desarrollo y pruebas
