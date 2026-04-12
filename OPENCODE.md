# Cerebro — Instrucciones para OpenCode

## Proyecto

Sistema de automatización personal. Scripts Python/Bash que corren via cron en un VPS privado accesible por Tailscale. Reemplazan workflows anteriores.

## Regla fundamental

**Siempre spec antes de código.** Antes de implementar cualquier script, debe existir su spec en `docs/specs/[nombre].md`. Si no existe, ejecutar `/escribir-spec` primero.

## Estructura del repositorio

| Carpeta | Propósito |
|---------|-----------|
| `docs/specs/` | Especificaciones de cada script. Una por script. |
| `scripts/` | Implementaciones. El nombre del archivo debe coincidir con el de su spec. |
| `docs/profiles/behaviors/` | Perfiles de comportamiento importados según la tarea. |
| `docs/profiles/envs/` | Plantillas de variables de entorno por entorno. |
| `.opencode/commands/` | Comandos slash disponibles en este proyecto. |

## Perfiles de comportamiento

@docs/profiles/behaviors/new-script.md
@docs/profiles/behaviors/debug.md
@docs/profiles/behaviors/refactor.md
@docs/profiles/behaviors/security.md

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
| `/escribir-spec [descripción]` | Genera una spec en `docs/specs/` desde una descripción |
| `/crear-script [nombre]` | Implementa el script a partir de `docs/specs/[nombre].md` |
| `/revisar-script [nombre]` | Revisa el script contra su spec |
| `/lint` | Ejecuta flake8 + black sobre `scripts/` |
| `/worktree-deliver` | Empaqueta cambios como PR con commit convencional |
| `/check-sensitive` | Revisa cambios pendientes en busca de información sensible |

## Entornos

Los scripts corren en dos entornos. Ver `docs/profiles/envs/` para las variables necesarias en cada uno.

- **vps**: Servidor principal (Ubuntu 24.04, red Tailscale)
- **local**: Estación de trabajo para desarrollo y pruebas

## Acceso SSH al VPS

Cuando necesites conectarte al VPS, usa **siempre** el alias de agente definido en `~/.ssh/config` para este proyecto. Ese alias conecta con un usuario de shell restringido y privilegios mínimos.

**Nunca uses el alias del usuario principal** — tiene acceso completo y requiere 2FA.
