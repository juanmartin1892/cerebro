# infra/mcp

Servidores MCP expuestos sobre SSE para Claude Code, accesibles únicamente desde la red Tailscale.

## Componentes

| Contenedor | Imagen | Propósito |
|---|---|---|
| `filesystem-mcp` | `node:20-alpine` | Servidor MCP (`@modelcontextprotocol/server-filesystem`) — vault de Obsidian |
| `grafana-mcp` | `ghcr.io/grafana/mcp-grafana:latest` | Servidor MCP para consultar métricas y logs vía Grafana |
| `mcp-caddy` | `caddy:2-alpine` | Reverse proxy HTTPS con cert Tailscale |

## Endpoints

| Servicio | Puerto | URL |
|---|---|---|
| vault (filesystem) | 3100 | `https://${TAILSCALE_HOST}:3100/sse` |
| grafana | 3101 | `https://${TAILSCALE_HOST}:3101/sse` |

## Configurar en Claude Code

```bash
claude mcp add --transport sse vault https://${TAILSCALE_HOST}:3100/sse
claude mcp add --transport sse grafana https://${TAILSCALE_HOST}:3101/sse
```

## Despliegue

```bash
cd ~/vault/proyectos/cerebro/infra/mcp
sudo docker compose up -d
sudo docker compose logs -f
```

## Variables de entorno

Ver `.env.example`. Copiar a `.env` y rellenar antes de arrancar.

| Variable | Propósito |
|---|---|
| `TAILSCALE_IP` | IP Tailscale del VPS — Caddy bind solo en esa interfaz |
| `TAILSCALE_HOST` | Hostname Tailscale (p.ej. `cerebro.tail3e4af2.ts.net`) |
| `VAULT_PATH` | Ruta absoluta al vault de Obsidian en el VPS |
| `GRAFANA_URL` | URL de Grafana (`http://<TAILSCALE_IP>:3001`) |
| `GRAFANA_API_KEY` | Token de service account de Grafana (rol Viewer) |

### Crear el service account de Grafana

1. Grafana → **Administration → Service accounts → Add service account**
2. Nombre: `claude-mcp`, Rol: `Viewer`
3. **Add service account token** → copiar el token a `GRAFANA_API_KEY` en `.env`

## Renovar el certificado Tailscale

Los certs Tailscale tienen una validez de ~90 días. Para renovar:

```bash
sudo tailscale cert --cert-file /etc/ssl/tailscale/cerebro.crt \
                    --key-file  /etc/ssl/tailscale/cerebro.key \
                    ${TAILSCALE_HOST}
sudo docker exec mcp-caddy caddy reload --config /etc/caddy/Caddyfile
```
