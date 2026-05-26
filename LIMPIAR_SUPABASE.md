# Limpieza de datos antiguos en Supabase

Si en Supabase ves filas que no ingresaste, probablemente son los datos del pipeline del Titanic o pruebas anteriores. Para borrar todo y dejar solo los registros nuevos, sigue estos pasos:

1. Abre Supabase y selecciona tu proyecto.
2. Ve a **SQL Editor**.
3. Abre el archivo `clean_supabase.sql` en este repositorio.
4. Copia y pega el contenido en el editor de Supabase.
5. Ejecuta el script.

El script elimina todos los registros de la tabla `titanic` y reinicia la secuencia de ids.

> Después de limpiar, vuelve a usar el formulario en `app.py` para ingresar solo los datos nuevos.

---

## Nota sobre `categorías`

El campo `categorías` ahora se calcula automáticamente desde `Clase de pasaje`:
- `1` → `Primero`
- `2` → `Segundo`
- `3` → `Tercero`

Esto corrige el problema de que `categorías` quedara en `NULL`.
