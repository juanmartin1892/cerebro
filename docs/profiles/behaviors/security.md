# Perfil: Seguridad de la información

## Regla fundamental

**Ningún documento fuera de `internal-docs/` debe contener información sensible.**

`internal-docs/` está en `.gitignore` y nunca se publica. Todo lo demás en el repo es público.

## Qué se considera información sensible

- IPs y direcciones de red reales
- Credenciales, API keys, tokens, contraseñas
- Nombres de usuario reales del sistema
- Claves SSH o certificados
- Detalles de configuración de seguridad que revelen la superficie de ataque

## Cómo escribir configuración y documentación

- Usar variables de entorno (`${VARIABLE}`) en lugar de valores reales en cualquier fichero versionado
- Usar placeholders genéricos en documentación (`<ip>`, `<usuario>`, `<dominio>`)
- Si hay duda sobre si algo es sensible, moverlo a `internal-docs/`

## Antes de cada commit o PR

Ejecutar `/check-sensitive` para detectar posibles fugas antes de publicar.
