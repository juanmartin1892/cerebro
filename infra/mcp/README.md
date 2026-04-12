# infra/mcp

Servidor MCP que expone el vault de Obsidian sobre SSE para Claude Code.

## Componentes

| Contenedor | Imagen | Propósito |
|---|---|---|
| `filesystem-mcp` | `node:20-alpine` | Servidor MCP (`@modelcontextprotocol/server-filesystem`) en puerto 3000 interno |
| `mcp-caddy` | `caddy:2-alpine` | Reverse proxy HTTPS con cert Tailscale, escucha en puerto 3100 |

## Endpoint

```
https://${TAILSCALE_HOST}:3100/sse
```

Solo accesible desde la red Tailscale.

## Configurar en Claude Code

```bash
claude mcp add --transport sse vault https://${TAILSCALE_HOST}:3100/sse
```

## Despliegue

```bash
cd ~/vault/proyectos/cerebro/infra/mcp
sudo docker compose up -d
sudo docker compose logs -f
```

## Renovar el certificado Tailscale

Los certs Tailscale tienen una validez de ~90 días. Para renovar:

```bash
sudo tailscale cert --cert-file /etc/ssl/tailscale/cerebro.crt \
                    --key-file  /etc/ssl/tailscale/cerebro.key \
                    ${TAILSCALE_HOST}
sudo docker exec mcp-caddy caddy reload --config /etc/caddy/Caddyfile
```

## Variables de entorno

Ver `.env.example`. La única variable requerida es `TAILSCALE_IP` para que Caddy bind solo en la interfaz Tailscale.
