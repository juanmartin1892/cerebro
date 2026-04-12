# Skill: Refactorizar un script

Cuando se refactoriza un script existente, respetar estas reglas.

## Reglas fundamentales

1. **No cambiar el comportamiento observable**: el script debe producir exactamente los mismos efectos secundarios y salidas tras el refactor.
2. **Mantener compatibilidad con el crontab**: no cambiar el nombre del script ni sus variables de entorno requeridas sin actualizar el crontab.
3. **Actualizar la spec si la interfaz cambia**: si el refactor cambia variables de entorno, entradas o salidas, actualizar `docs/specs/[nombre].md` antes o junto con el código.

## Proceso

1. Leer la spec en `docs/specs/[nombre].md` para entender el contrato del script.
2. Leer el script completo antes de proponer cambios.
3. Refactorizar manteniendo el contrato.
4. Verificar que el script sigue siendo ejecutable sin argumentos.
5. Si cambia algo observable, actualizar la spec primero y avisar al usuario.

## Qué sí se puede mejorar sin restricciones

- Estructura interna del código
- Claridad de nombres de variables y funciones
- Manejo de errores más robusto
- Logging más informativo
- Eliminar código duplicado

## Qué requiere confirmación del usuario

- Cambiar el nombre del archivo (implica actualizar crontab)
- Añadir o eliminar variables de entorno requeridas
- Cambiar el exit code en algún escenario
- Modificar el formato de la salida si otro proceso la consume
