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

[Acceso SSH al VPS]
  ├── Agentes IA (Claude Code / OpenCode)
  │     └── usuario restringido (rbash, sudoers acotados, solo clave SSH)
  └── Usuario humano
        └── usuario principal (clave SSH + TOTP)
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

### [2026-04-12] Usuario SSH restringido para agentes IA
- **Qué**: usuario dedicado con shell restringido (`rbash`) y sudoers mínimos para los agentes IA (Claude Code, OpenCode)
- **Por qué**: blast radius acotado si un agente se comporta mal; revocación inmediata borrando su `authorized_keys`; accesos auditables en `auth.log` diferenciados del usuario principal; principle of least privilege
- **Alternativas descartadas**: usuario principal compartido con los agentes (sin aislamiento, sin auditoría diferenciada)

### [2026-04-12] Stack de observabilidad: Prometheus + Grafana + Loki
- **Qué**: Prometheus (métricas) + node_exporter + Loki (logs) + Promtail (recolector) + Grafana (visualización), desplegados en Docker en el VPS bajo `infra/observability/`
- **Por qué**: suficiente para el caso de uso (VPS personal, logs SSH, métricas del sistema) sin el coste en RAM de Elastic (~1.5GB vs ~600MB). Grafana tiene integración OIDC nativa con Keycloak, que es el objetivo de la Fase 1.
- **Alternativa descartada**: ELK stack (Elasticsearch + Kibana) — excesivo en RAM para un CPX22, y Kibana requiere licencia X-Pack para OIDC
- **Acceso**: Grafana en `http://<tailscale-ip>:3001`, solo dentro de Tailscale
- **Configuración**: `infra/observability/` en el repo. IP y contraseña en `.env` (gitignored)
- **Estado**: operativo — métricas de CPU y logs SSH (`auth_log`) fluyendo a Grafana

### [2026-04-12] SearXNG eliminado de OpenClaw
- **Qué**: contenedor `searxng` y volumen `searxng_data` eliminados del docker-compose de OpenClaw
- **Por qué**: OpenClaw usa Brave Search (plugin activo con API key) — SearXNG estaba instalado por el script de setup por defecto pero no se usaba, consumiendo ~100MB RAM sin utilidad

### [2026-04-12] 2FA TOTP para el usuario principal
- **Qué**: autenticación en dos pasos para el usuario humano: clave SSH + código TOTP via `libpam-google-authenticator`; agentes usan solo clave (sin TOTP, no pueden interactuar con prompts)
- **Por qué**: la clave SSH puede verse comprometida (máquina robada, clave exportada); TOTP añade un segundo factor independiente del dispositivo
- **Alternativas descartadas**: solo clave SSH (factor único); contraseña + TOTP sin clave (menos seguro que publickey)

### [2026-04-13] fail2ban para mitigación de fuerza bruta SSH
- **Qué**: fail2ban monitoriza `/var/log/auth.log` y banea automáticamente IPs que superan el umbral de fallos de autenticación añadiendo reglas a ufw. Configurado con `bantime=1d`, `findtime=10m`, `maxretry=5` — más agresivo que los defaults para reducir el ruido.
- **Por qué**: cualquier VPS con puerto 22 expuesto recibe fuerza bruta continua de forma inevitable. fail2ban es el estándar para mitigarlo sin intervención manual. El 2FA y la autenticación por clave impiden el acceso real, pero sin fail2ban los intentos consumen recursos del sshd y saturan los logs.
- **Alternativas descartadas**: sshguard (solo SSH, menos configurable), CrowdSec (más potente con inteligencia comunitaria, pero mayor complejidad operativa para este caso de uso), ufw manual (sin expiración automática de bans)
- **Configuración**: `/etc/fail2ban/jail.local` en el VPS (no versionado — contiene detalles del entorno)