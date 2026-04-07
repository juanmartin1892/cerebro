Ejecuta linters sobre los scripts del proyecto.

Pasos:
1. Ejecuta `flake8 scripts/` para detectar errores de estilo y posibles bugs.
2. Ejecuta `black --check scripts/` para detectar problemas de formato (sin modificar archivos aún).
3. Muéstrame el resultado.
4. Si hay errores de formato de black, pregúntame si quiero aplicar `black scripts/` para corregirlos automáticamente.
5. Los errores de flake8 deben corregirse manualmente — señálalos con el contexto necesario para entenderlos.

Si flake8 o black no están instalados: `pip install flake8 black`.
