# Configuraciones de entorno

Cada entorno donde corren los scripts tiene su propio conjunto de variables de entorno.

## Uso

1. Copiar el archivo `.env.example` del entorno correspondiente:
   ```bash
   cp profiles/envs/vps.env.example profiles/envs/vps.env
   cp profiles/envs/local.env.example profiles/envs/local.env
   ```

2. Rellenar los valores reales en el archivo `.env` copiado.

3. Los archivos `.env` reales están en `.gitignore` — nunca se suben a GitHub.

## Cargar las variables

```bash
# Cargar antes de ejecutar un script manualmente
set -a && source profiles/envs/vps.env && set +a
python3 scripts/nombre-script.py
```

Para el cron, definir las variables directamente en el crontab o en `/etc/environment`.

## Entornos disponibles

| Archivo | Entorno |
|---------|---------|
| `vps.env.example` | Servidor principal (Ubuntu, Tailscale) |
| `local.env.example` | Estación de trabajo local (desarrollo) |
