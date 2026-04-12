# Arquitectura

## Diagrama
```
[Telegram móvil]
      ↓
[OpenClaw - Docker - VPS]
  └── Kimi K2.5 via OpenCode Zen
      ├── lee /workspace/vault/
      └── escribe /workspace/vault/
              ↕ Syncthing
      ~/vault en CachyOS y Android
              ↕
         Obsidian (visor)

[cron - VPS]
  └── scripts/Python → logs /var/log/cerebro/
```

## Decisiones tomadas

### [2026-03-19] OpenClaw como motor agéntico
- **Qué**: agente self-hosted con acceso nativo al filesystem
- **Por qué**: lectura y escritura de .md sin intermediarios, interfaz via Telegram, sin necesidad de web UI
- **Alternativas descartadas**: Khoj (problemas con OpenCode Zen y extended thinking), Dify (no escribe ficheros nativamente)

### [2026-03-19] Syncthing como capa de sincronización
- **Qué**: sincronización P2P de ficheros .md entre dispositivos
- **Por qué**: ficheros reales en disco, sin base de datos intermedia, compatible con Obsidian
- **Alternativas descartadas**: CouchDB + LiveSync (vault opaco, incompatible con acceso directo del agente)

### [2026-03-19] Kimi K2.5 como modelo principal
- **Qué**: modelo open source de Moonshot AI via OpenCode Zen
- **Por qué**: $0.40/$2.50 por millón de tokens, capacidades agénticas sólidas, sin problemas de extended thinking
- **Alternativas descartadas**: Claude Sonnet 4.5 (error 400 con OpenCode Zen), Claude Sonnet 4.6 (extended thinking no soportado por Zen)

### [2026-03-19] Vault en filesystem del host
- **Qué**: vault del host montado como volumen en OpenClaw
- **Por qué**: fuente de verdad única, accesible por Syncthing y OpenClaw simultáneamente sin duplicación
- **Alternativas descartadas**: vault dentro de volumen Docker (opaco, no accesible por Syncthing)

### [2026-03-19] Kimi Search como proveedor de búsqueda web
- **Qué**: búsqueda web integrada via Moonshot AI
- **Por qué**: misma cuenta que el modelo principal, sin tarjeta adicional, integración nativa en OpenClaw
- **Alternativas descartadas**: Brave Search (requiere tarjeta), SearXNG (no soportado nativamente en el wizard de OpenClaw)

### [2026-03-25] n8n como motor de workflows _(descartado 2026-04-09)_
- **Qué**: n8n self-hosted en Docker con SQLite, vault montado en /vault, puerto 5678
- **Por qué se instaló**: automatización de workflows, integración con agente, acceso al filesystem del vault
- **Por qué se desinstalió**: los scripts Python ejecutados via cron resultaron más adecuados para el perfil del proyecto. n8n añadía complejidad operativa (UI, contenedor permanente, SQLite, actualizaciones) sin aportar ventajas reales frente a scripts directos. Los workflows de n8n son opacos y difíciles de versionar; los scripts cron son código Python en git.
- **Decisión final**: desinstalado el 2026-04-09. La automatización queda 100% en `scripts/` con cron.

### [2026-04-09] Scripts Python + cron como capa de automatización
- **Qué**: scripts Python en `scripts/`, ejecutados por cron en el VPS, logs en `/var/log/cerebro/`
- **Por qué**: más simples que n8n, versionables en git, sin dependencias de UI ni contenedores adicionales, alineados con el perfil técnico del proyecto
- **Proceso**: spec en `specs/` → implementación en `scripts/` → cron entry → logs