"""Simple orchestration for the DataOps pipeline."""
import logging
from src import ingestion, processing, validation, load

LOG = logging.getLogger("pipeline")

def run():
    logging.basicConfig(level=logging.INFO)
    LOG.info("Iniciando pipeline")
    raw = ingestion.fetch_titanic()
    processed = processing.clean_transform(raw_path=raw)
    validation.validate_schema(processed)
    db = load.load_to_sqlite(processed)
    LOG.info("Pipeline finalizado. BD en %s", db)

if __name__ == "__main__":
    run()
