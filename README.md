# Evaluación Parcial N°2 — Pipeline de datos (Titanic)

## Resumen
Proyecto que implementa un pipeline reproducible para procesamiento de datos del dataset Titanic. Incluye etapas de ingesta, limpieza y transformación, validación, carga a base de datos y una pequeña demo web para visualizar KPIs.

## Objetivo
Demostrar un flujo de trabajo de ingeniería de datos que permita:
- Preparar y limpiar datos de entrada.
- Validar la calidad y estructura del dataset.
- Cargar los datos en una base local (SQLite) o remota (Postgres/Supabase).
- Exponer indicadores básicos mediante una API/mini-app.

## Estructura principal
- `src/` — código del pipeline:
  - `ingestion.py` — descarga o lectura del dataset y guarda en `data/raw`.
  - `processing.py` — limpieza y transformaciones; guarda resultado en `data/processed`.
  - `validation.py` — validaciones de esquema y controles básicos.
  - `load.py` — carga de datos en SQLite o Postgres (según variables de entorno).
  - `pipeline.py` — orquestador que ejecuta las etapas en secuencia.
- `app.py` — API/mini-app en Flask con endpoints para KPIs y estado de la base.
- `data/` — carpetas `raw/`, `processed/` y `db/`.
- `docs/` — plantilla de informe y material de entrega.
- `tests/` — pruebas con `pytest`.
- `Dockerfile`, `requirements.txt`, `setup_and_run.ps1` — utilidades y scripts.

## Requisitos
- Python 3.11+ (funciona con Python 3.8+ en la práctica).
- Dependencias listadas en `requirements.txt`.

## Instalación rápida (Windows PowerShell)
1. Clonar el repositorio y entrar a la carpeta:
```powershell
git clone https://github.com/Symxnmf/Evaluacion-2Gestion-de-datos-para-IA.git
cd Evaluacion-2Gestion-de-datos-para-IA
```

2. Crear y activar un entorno virtual:
```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instalar dependencias:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## Uso
- Ejecutar el pipeline completo:
```powershell
python -m src.pipeline
```

- Iniciar la demo web:
```powershell
python app.py
```

La demo expone al menos los endpoints:
- `GET /status` — indica si la base de datos está disponible.
- `GET /kpis` — devuelve KPIs básicos: `filas_totales`, `edad_promedio`, `edad_faltante`, `tasa_supervivencia`.

Si prefieres usar PostgreSQL o Supabase, define en un archivo `.env` las variables `DATABASE_URL` o `SUPABASE_URL` y `SUPABASE_KEY`.

## Datos
- Datos de entrada: `data/raw/titanic.csv`.
- Datos procesados: `data/processed/titanic_clean.csv`.
- Base local SQLite: `data/db/titanic.db` (si no se usa backend remoto).

## Scripts y utilidades
- `setup_and_run.ps1` — script para automatizar entorno e inicio en PowerShell.
- `Dockerfile` — imagen para ejecutar la app en contenedor.
- `clean_supabase.sql`, `rename_columns.sql` — scripts SQL auxiliares incluidos en la raíz.

## Pruebas
Ejecutar las pruebas unitarias con `pytest`:
```powershell
pytest -q
```

## Buenas prácticas
- No subir credenciales; usa `.env` para variables sensibles.
- Para despliegue en producción, usar un servidor WSGI (por ejemplo `gunicorn`) y contenedores.

## Licencia
Puedes añadir un archivo `LICENSE` si deseas publicar el proyecto bajo MIT u otra licencia.

## Contacto
Si necesitas adaptaciones (por ejemplo cambiar la fuente de datos o añadir nuevas validaciones), abre una issue o contacta al autor del repositorio.