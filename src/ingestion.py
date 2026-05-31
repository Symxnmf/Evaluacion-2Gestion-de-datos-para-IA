import os
import logging
import seaborn as sns

LOG = logging.getLogger("ingestion")


def ensure_dirs():
    # Crear directorios necesarios para raw data y logs
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("logs", exist_ok=True)


def fetch_titanic(save_path="data/raw/titanic.csv"):
    """Carga el dataset `titanic` desde la librería seaborn y lo guarda en CSV.

    Retorna la ruta del archivo guardado. Esta función es el punto de ingesta
    usado por el pipeline (descarga/obtención de datos de entrada).
    """
    ensure_dirs()
    # seaborn incluye el dataset 'titanic' como ejemplo; se usa aquí para la demo
    df = sns.load_dataset("titanic")
    # Guardar datos crudos para etapas posteriores
    df.to_csv(save_path, index=False)
    LOG.info("Dataset Titanic guardado en %s", save_path)
    return save_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetch_titanic()
