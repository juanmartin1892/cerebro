# Cerebro — Second Brain Personal

## Descripción

Sistema agéntico personal para gestión de conocimiento, investigación y generación de documentos. Combina un vault de notas Markdown con un agente de IA accesible desde Telegram.

## Estado

Activo — en construcción iterativa

## Stack

- **Agente IA**: OpenClaw (Docker)
- **Automatización**: Scripts Python/Bash ejecutados via cron
- **Vault de notas**: Obsidian + Syncthing
- **Interfaz**: Telegram bot
- **LLM**: Kimi K2.5

## Scripts

Los scripts en `scripts/` reemplazan workflows anteriores de n8n. Cada script tiene una función específica y se ejecuta mediante cron en el servidor principal.

Ver `scripts/README.md` para detalles de configuración y uso.

## Última actualización

2026-04-07
