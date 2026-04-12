Empaqueta los cambios del worktree actual como un pull request.

Sigue la especificación en `docs/specs/worktree-deliver.md` para el formato de mensajes.

Pasos:
1. Verifica que estás en un worktree (no en `main`). Si estás en `main`, avisa y detente.
2. Ejecuta `/check-sensitive` antes de continuar. Si detecta información sensible, detente y corrígela antes de seguir.
2. Muestra los cambios pendientes con `git status` y `git diff --stat`.
3. Analiza el contenido con `git diff` para entender qué cambios se introducen.
4. Propón un mensaje de PR siguiendo el formato de la spec:
   - **Título:** `<type>: <descripción>` (máx 50 chars, conventional commits)
   - **Cuerpo:** Estructura Markdown con Summary, Changes, Context
   - Tipos: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`
5. Muestra el mensaje completo propuesto (título + cuerpo) y pide confirmación.
6. Tras confirmar: `git add -A`, `git commit -m "título" -m "cuerpo"`, `git push`, `gh pr create --title "..." --body "..."`.
7. Devuelve la URL del PR creado.
