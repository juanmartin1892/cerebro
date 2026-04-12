# Spec: [nombre-del-script]

## Propósito

[Descripción en 1-2 frases de qué hace este script y por qué existe.]

## Cron schedule

```cron
# m h dom mon dow command
0 * * * *  /path/to/scripts/nombre-del-script.py >> /var/log/cerebro/nombre-del-script.log 2>&1
```

## Entradas

### Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `EJEMPLO_API_KEY` | Clave de API del servicio X | `abc123` |

### Variables de entorno opcionales

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `LOG_LEVEL` | Nivel de logging | `INFO` |

### Archivos de entrada

- (ninguno / describir si aplica)

## Salidas

### Stdout / log

- [Qué imprime el script en ejecución normal]
- [Qué imprime en caso de error]

### Archivos generados

- (ninguno / describir si aplica)

### Efectos secundarios

- [Llamadas a APIs externas, mensajes enviados, archivos modificados, etc.]

## Dependencias Python

```
# requirements (añadir a requirements.txt del proyecto si aplica)
requests>=2.31
```

## Comportamiento ante errores

- **Error de red**: reintentar N veces con backoff exponencial, luego salir con código 1
- **Credencial inválida**: salir inmediatamente con código 1 y mensaje claro
- **[Otro caso]**: [comportamiento esperado]

## Notas de implementación

- [Cualquier detalle técnico relevante para la implementación]
- [Limitaciones conocidas o casos borde a tener en cuenta]
