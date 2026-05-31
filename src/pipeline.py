"""Orquestador sencillo para el pipeline de datos.

Ejecuta las etapas en orden: ingesta -> procesamiento -> validación -> carga.
La carga delega según variables de entorno a Postgres/Supabase o a SQLite local.
"""
import logging
from src import ingestion, processing, validation, load

LOG = logging.getLogger("pipeline")


def run():
    # Configuración básica de logging y ejecución en secuencia
    logging.basicConfig(level=logging.INFO)
    LOG.info("Iniciando pipeline")
    # 1) Ingesta: obtiene la ruta del CSV crudo
    raw = ingestion.fetch_titanic()
    # 2) Procesamiento: aplica transformaciones y devuelve ruta del CSV procesado
    processed = processing.clean_transform(raw_path=raw)
    # 3) Validación: asegúrate que el CSV procesado cumple el esquema esperado
    validation.validate_schema(processed)
    # 4) Carga: escribe en la base configurada (remote o local)
    db_location = load.load_to_database(processed)
    LOG.info("Pipeline finalizado. Resultado en %s", db_location)


if __name__ == "__main__":
    run()
