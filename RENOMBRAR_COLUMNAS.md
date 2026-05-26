# 📋 Instrucciones: Renombrar columnas en Supabase a español

## Paso 1: Abrir SQL Editor en Supabase

1. Ve a tu proyecto Supabase: https://app.supabase.com
2. En el menú lateral, selecciona **SQL Editor**
3. Haz clic en **New Query** o **+ New**

## Paso 2: Copiar y ejecutar el script

Abre el archivo `rename_columns.sql` (está en la raíz del proyecto) y copia TODO el contenido.

Luego pega en el SQL Editor de Supabase y haz clic en **Run**.

El script hará estos cambios:

| Nombre actual (inglés) | Nuevo nombre (español) |
|---|---|
| `survived` | `sobrevivio` |
| `pclass` | `clase` |
| `sex` | `sexo` |
| `age` | `edad` |
| `sibsp` | `hermanos_cony` |
| `parch` | `padres_hijos` |
| `fare` | `tarifa` |
| `embarked` | `puerto_embarque` |
| `who` | `quien` |
| `adult_male` | `adulto_hombre` |
| `embark_town` | `ciudad_puerto` |
| `alone` | `solo_a` |
| `class` | `categorías` |

## Paso 3: Verificar cambios

Después de ejecutar, ve a la tabla `titanic` en **Table Editor** y verás que todas las columnas están en español.

## Paso 4: Usar el nuevo formulario

Ahora cuando:
- Ejecutes el pipeline: `python -m src.pipeline` → subirá datos con nombres españoles
- Abras la demo: `python app.py` → el formulario enviará datos con nombres españoles

¡Todo estará listo en español! 🚀
