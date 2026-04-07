# Perfil: Crear nuevo script

Cuando se crea un nuevo script, seguir este proceso:

## 1. Leer la spec completa

Antes de escribir una sola línea de código, leer `specs/[nombre].md` en su totalidad. Si la spec no existe, detener y pedir al usuario que ejecute `/escribir-spec` primero.

## 2. Estructura obligatoria del script Python

```python
#!/usr/bin/env python3
"""
[nombre-del-script].py — [descripción breve del propósito]

Cron: m h dom mon dow /path/to/scripts/[nombre].py >> /var/log/cerebro/[nombre].log 2>&1
"""

import logging
import os
import sys

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def main() -> None:
    # Leer config desde env vars — nunca hardcodear credenciales
    api_key = os.environ.get("EJEMPLO_API_KEY")
    if not api_key:
        log.error("EJEMPLO_API_KEY no está definida")
        sys.exit(1)

    # Lógica principal aquí
    ...


if __name__ == "__main__":
    main()
```

## 3. Reglas de implementación

- **Credenciales**: solo via `os.environ`. Salir con `sys.exit(1)` si falta alguna requerida.
- **Logging**: usar `log.info()`, `log.warning()`, `log.error()`. Nunca `print()`.
- **Errores**: capturar excepciones específicas, no usar `except Exception` en blanco.
- **Idempotencia**: el script debe poder ejecutarse dos veces seguidas sin efectos duplicados si es posible.
- **Exit codes**: `0` para éxito, `1` para error.

## 4. Al terminar

- Añadir el script a `scripts/README.md` con su nombre, propósito y cron schedule.
- Verificar que el nombre del archivo `.py` coincide exactamente con el nombre en la spec.
