Empaqueta los cambios del worktree actual como un pull request.

Pasos:
1. Verifica que estás en un worktree (no en `main`). Si estás en `main`, avisa y detente.
2. Muestra los cambios pendientes con `git diff` y `git status`.
3. Propón un mensaje de commit siguiendo conventional commits:
   - `feat:` — nueva funcionalidad (nuevo script, nuevo comando)
   - `fix:` — corrección de bug
   - `refactor:` — refactor sin cambio de comportamiento
   - `docs:` — solo cambios en specs, README, CLAUDE.md
   - `chore:` — mantenimiento (actualizar .gitignore, etc.)
4. Muéstrame el mensaje de commit propuesto y pide confirmación.
5. Tras confirmar: `git add -A`, `git commit`, `git push`, `gh pr create`.
6. Devuelve la URL del PR creado.
