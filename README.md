# Evaluación Parcial N°2 — Pipeline DataOps

## Descripción corta
Pipeline DataOps reproducible aplicado al dataset `Titanic` (ejemplo). Implementa las etapas de ingesta, limpieza y transformación, validación, carga y una demo web para mostrar KPIs.

## Por qué existe este proyecto
Este repositorio es la entrega de la Evaluación Parcial N°2 del curso de Gestión de Datos para IA. Busca demostrar un flujo de trabajo DataOps completo y ordenado, con código funcional, evidencia técnica y una demo que sirva para la defensa oral.

## Estado actual
- Código funcional en Python 3.11+.
- Entorno reproducible con `requirements.txt` y `Dockerfile`.
- Demo Flask disponible en `http://127.0.0.1:5000` con endpoints `/kpis` y `/status`.

## Equipo y reparto 50/50
| Integrante | Rol principal | Aporte |
|---|---|---|
| Simon | Desarrollo técnico / Data Engineer | Implementación del pipeline DataOps: ingesta, limpieza, validación, carga, pruebas funcionales y apoyo en la demo. |
| Benja | Documentación / DevOps / Presentación | Redacción del README, plantilla del informe, organización del repositorio, apoyo en la demo y preparación de la presentación. |

- Reparto general: 50% Simon y 50% Benja.
- Ambos revisaron las partes principales para mantener coherencia técnica y de presentación.

## Ramas del proyecto
- `main` — versión integrada final con todo el proyecto junto.
- `Simon` / `simon` — rama enfocada en la parte técnica del pipeline y la demo.
- `Benja` / `benja` — rama enfocada en documentación, organización y presentación.

## Contenido y estructura
- `src/` — implementaciones del pipeline:
  - `ingestion.py` — ingesta (descarga dataset de ejemplo y guarda en `data/raw`).
  - `processing.py` — limpieza y transformaciones básicas, salida en `data/processed`.
  - `validation.py` — validaciones estructurales y semánticas.
  - `load.py` — carga a SQLite (`data/db/titanic.db`).
  - `pipeline.py` — orquestador que ejecuta las etapas.
- `app.py` — API/demo con Flask.
- `data/` — directorios `raw`, `processed`, `db`.
- `docs/` — plantilla de informe y recursos de entrega.
- `tests/` — pruebas básicas con `pytest`.
- `Dockerfile`, `requirements.txt`, `setup_and_run.ps1` — utilidades y scripts.

## Instalación rápida en Windows PowerShell
1. Clonar el repositorio y entrar a la carpeta:
```powershell
git clone https://github.com/Symxnmf/Evaluacion-2Gestion-de-datos-para-IA.git
cd Evaluacion-2Gestion-de-datos-para-IA
```

2. Crear y activar el entorno virtual:
```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instalar dependencias:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. Ejecutar el pipeline completo:
```powershell
python -m src.pipeline
```

5. Levantar la demo:
```powershell
python app.py
```

Luego abrir en el navegador:
```text
http://127.0.0.1:5000/kpis
```

## Atajo
El archivo `setup_and_run.ps1` automatiza la creación del entorno, la instalación de dependencias y la ejecución del pipeline.

## Uso con Docker
Construir imagen:
```powershell
docker build -t dataops-demo:latest .
```

Ejecutar contenedor:
```powershell
docker run -p 5000:5000 dataops-demo:latest
```

## Endpoints de la demo
- `GET /status` — devuelve `{ "bd_existe": true/false }`.
- `GET /kpis` — devuelve KPIs básicos: `filas_totales`, `edad_promedio`, `edad_faltante`, `tasa_supervivencia`.

## Evidencias y entregables
- `data/db/titanic.db` — base de datos generada por el pipeline.
- `data/processed/titanic_clean.csv` — datos procesados.
- `docs/Informe_template.md` — plantilla para completar el informe PDF.
- `app.py` — demo web funcional.

## Buenas prácticas y seguridad
- No subir credenciales ni archivos sensibles. `venv/` ya está en `.gitignore`.
- Para producción, usar contenedores y un servidor WSGI como `gunicorn` en lugar del servidor de desarrollo de Flask.

## Licencia
Se puede publicar con licencia MIT si quieres compartir el código abierto. Añade un archivo `LICENSE` si lo necesitas.

## Contacto
Si quieres que personalice el informe o la presentación, puedo generarlos a partir de esta base.

## Recordatorio final
Antes de exportar a PDF, completa `docs/Informe_template.md` con portada, nombres, fechas y capturas.