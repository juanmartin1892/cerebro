Revisa los cambios pendientes de commit en busca de información sensible antes de publicar.

Pasos:

1. Obtén los ficheros que se publicarían con `git diff --name-only` y `git ls-files --others --exclude-standard` (untracked).
2. Excluye los ficheros que ya están cubiertos por `.gitignore` (`internal-docs/`, `*.env`, etc.).
3. Para los ficheros restantes, analiza el contenido con `git diff` y lee los ficheros nuevos buscando:
   - IPs o rangos de red (patrones como `\d+\.\d+\.\d+\.\d+`)
   - Tokens, API keys o contraseñas (patrones como `key`, `token`, `secret`, `password`, `Bearer` seguidos de valores reales, no placeholders)
   - Nombres de usuario del sistema fuera de `internal-docs/`
   - Cualquier valor que debería estar en un `.env` pero está hardcodeado
4. Si encuentras algo sospechoso: muéstralo, explica por qué es sensible y propón cómo corregirlo (mover a `.env`, usar placeholder, mover a `internal-docs/`).
5. Si todo está limpio: confirma explícitamente que no se detectó información sensible y es seguro hacer commit.
