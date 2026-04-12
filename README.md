# Cerebro — Second Brain Personal

## Descripción

Sistema agéntico personal para gestión de conocimiento, investigación y generación de documentos. Combina un vault de notas Markdown con un agente de IA accesible desde Telegram.

## Estado

Activo — en construcción iterativa

## Stack

- **Agente IA**: OpenClaw (Docker)
- **Automatización**: Scripts Python/Bash ejecutados via cron (ver `scripts/`)
- **Vault de notas**: Obsidian + Syncthing
- **Interfaz**: Telegram bot
- **LLM**: Kimi K2.5

## Estructura del repositorio

```
cerebro/
├── CLAUDE.md              # Configuración de Claude Code para este proyecto
├── OPENCODE.md            # Configuración de OpenCode para este proyecto
├── docs/
│   ├── arquitectura.md    # Diagrama del sistema y decisiones de diseño
│   ├── specs/             # Especificación de cada script (una por script)
│   │   └── _template.md   # Plantilla para nuevas specs
│   └── profiles/
│       ├── behaviors/     # Perfiles de comportamiento de Claude Code
│       └── envs/          # Plantillas de variables de entorno por entorno
├── scripts/               # Implementaciones (Python/Bash)
├── .claude/commands/      # Comandos slash disponibles en Claude Code
└── .opencode/commands/    # Comandos slash disponibles en OpenCode
```

## Flujo de trabajo

1. Describir el script con `/escribir-spec`
2. Implementarlo con `/crear-script`
3. Revisarlo con `/revisar-script`
4. Entregar cambios con `/worktree-deliver`

## Última actualización

2026-04-12
