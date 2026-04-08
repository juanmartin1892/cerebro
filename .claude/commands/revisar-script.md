Revisa el script `scripts/$ARGUMENTS.py` contra su spec y las convenciones del proyecto.

Sigue estos pasos:
1. Lee `specs/$ARGUMENTS.md` para entender el contrato del script.
2. Lee `scripts/$ARGUMENTS.py`.
3. Comprueba:
   - ¿El script implementa todo lo que describe la spec?
   - ¿Usa `logging` en lugar de `print`?
   - ¿Todas las credenciales vienen de `os.environ`?
   - ¿Tiene `main()` y `if __name__ == "__main__"`?
   - ¿El manejo de errores cubre los casos descritos en la spec?
   - ¿Sale con código 1 en error y 0 en éxito?
4. Entrega un informe con: ✅ lo que está bien, ⚠️ mejoras recomendadas, ❌ problemas que hay que corregir.
5. Pregúntame si quieres que aplique las correcciones.
