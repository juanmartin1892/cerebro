# Spec: worktree-deliver

## Propósito

Estandarizar el proceso de creación de merge requests/pull requests para que tanto Claude Code como OpenCode generen mensajes consistentes y de alta calidad.

## Formato de Mensaje de MR/PR

### Título

Sigue [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <descripción corta en imperativo presente>
```

**Tipos permitidos:**

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `feat` | Nueva funcionalidad (script, comando, skill) | `feat: add script for backup automation` |
| `fix` | Corrección de bug | `fix: resolve API timeout in notify script` |
| `refactor` | Cambio de estructura sin cambiar comportamiento | `refactor: split monolithic script into modules` |
| `docs` | Cambios solo en documentación | `docs: update README with setup instructions` |
| `chore` | Mantenimiento, configuración, dependencias | `chore: update .gitignore for Python cache` |
| `test` | Adición o corrección de tests | `test: add unit tests for parser module` |

**Reglas para el título:**
- Máximo 50 caracteres después del tipo
- No poner punto final
- Usar imperativo presente ("add", "fix", "update", no "added", "fixed", "updating")

### Cuerpo

Estructura en Markdown:

```markdown
## Summary

[Breve descripción de qué cambios introduce este PR en 1-2 oraciones.]

## Changes

- [Cambio específico con contexto suficiente para entender el "qué" y "por qué"]
- [Otro cambio, con detalles técnicos si son relevantes]
- [Cambio adicional, enlazando a issues o specs relacionadas si aplica: ver #3, specs/notify.md]

## Context

[Explicación adicional de por qué se hizo este cambio, decisiones técnicas tomadas, 
limitaciones conocidas, o referencias a conversaciones previas. Opcional si el 
Summary y Changes son suficientemente descriptivos.]
```

**Reglas para el cuerpo:**
- Usar líneas de máximo 72 caracteres
- Bullet points en Changes deben ser específicos, no genéricos (evitar "varios cambios", "actualizaciones diversas")
- Incluir referencias a archivos específicos cuando ayude al revisor

## Proceso de Ejecución

1. **Verificación de rama:** Confirmar que NO se está en `main`. Si se está en main, abortar y pedir al usuario que cree un worktree primero.

2. **Análisis de cambios:**
   - Ejecutar `git status` y `git diff --stat` para ver el alcance
   - Ejecutar `git diff` para ver el contenido real
   - Identificar qué archivos se crearon/modificaron/eliminaron

3. **Clasificación del cambio:**
   - Determinar el tipo de conventional commit apropiado
   - Si hay múltiples tipos de cambios, priorizar: `feat` > `fix` > `refactor` > `test` > `docs` > `chore`
   - O considerar si deberían ser commits separados

4. **Propuesta al usuario:**
   - Mostrar el título propuesto
   - Mostrar el cuerpo completo propuesto
   - Preguntar: "¿Confirmas este mensaje? (s/n/modificar)"
   - Si el usuario elige "modificar", preguntar qué parte quiere cambiar

5. **Ejecución (tras confirmación):**
   ```bash
   git add -A
   git commit -m "<título>" -m "<cuerpo>"
   git push -u origin <rama-actual>
   gh pr create --title "<título>" --body "<cuerpo>"
   ```

6. **Resultado:** Devolver la URL del PR creado

## Notas de implementación

- El cuerpo del PR debe incluir la estructura completa (Summary, Changes, Context) aunque algunas secciones estén vacías o sean mínimas
- Para cambios triviales (ej: fix typo en README), se permite un cuerpo mínimo solo con Summary
- Si hay múltiples commits en la rama, el PR debe describir el resultado final, no cada commit individual
- Usar `gh pr create` con los flags `--title` y `--body` para evitar prompts interactivos
