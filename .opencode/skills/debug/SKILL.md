# Skill: Depurar un script

Cuando un script falla o produce resultados incorrectos, seguir este orden de diagnóstico.

## 1. Leer los logs

```bash
# Ver últimas ejecuciones del script

# Buscar errores
```

## 2. Verificar variables de entorno

Confirmar que todas las variables requeridas (listadas en la spec) están definidas en el entorno donde corre el cron:

```bash
# En el crontab o en el entorno del proceso cron
```

Si el cron corre como root o como otro usuario, su entorno puede diferir del shell interactivo.

## 3. Reproducir manualmente

Ejecutar el script de forma interactiva con las mismas variables de entorno:

```bash
LOG_LEVEL=DEBUG EJEMPLO_API_KEY=xxx python3 scripts/[nombre].py
```

`LOG_LEVEL=DEBUG` activa mensajes adicionales que ayudan a trazar el flujo.

## 4. Verificar conectividad (si el error es de red)

```bash
# Desde el VPS via Tailscale
curl -s https://api.servicio.com/health
ping -c 3 servicio.com
```

## 5. Antes de hacer cambios

- Leer la spec en `specs/[nombre].md` para confirmar el comportamiento esperado
- No cambiar el comportamiento del script para "esquivar" el error — encontrar la causa raíz
