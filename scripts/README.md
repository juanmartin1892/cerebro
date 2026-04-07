# Scripts de automatización — cerebro

Scripts que reemplazan los workflows de n8n. Se ejecutan via cron en el servidor principal.

## Estructura

```
scripts/
└── README.md   (este archivo)
```

## Añadir un nuevo script

1. Crear el script en esta carpeta
2. Documentarlo aquí (nombre, qué hace, frecuencia de ejecución)
3. Añadir la entrada al crontab del servidor: `crontab -e`

## Configuración de cron

Los scripts se ejecutan en el servidor principal. Plantilla para crontab:

```cron
# m h dom mon dow command
0 * * * *  /path/to/scripts/nombre-script.py >> /var/log/cerebro/nombre-script.log 2>&1
```

## Variables de entorno

Los scripts que necesiten credenciales las leen de variables de entorno o de un archivo `.env` local (nunca subido a git).
