"""Simple orchestration for the DataOps pipeline.

This orchestration uses the loader's `load_to_database` function which will
upload to a remote Postgres when `DATABASE_URL` (or SUPABASE credentials)
are present, otherwise falls back to SQLite local database.
"""
import logging
from src import ingestion, processing, validation, load

LOG = logging.getLogger("pipeline")


def run():
    logging.basicConfig(level=logging.INFO)
    LOG.info("Iniciando pipeline")
    raw = ingestion.fetch_titanic()
    processed = processing.clean_transform(raw_path=raw)
    validation.validate_schema(processed)
    db_location = load.load_to_database(processed)
    LOG.info("Pipeline finalizado. Resultado en %s", db_location)


if __name__ == "__main__":
    run()
