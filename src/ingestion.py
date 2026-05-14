import os
import logging
import seaborn as sns

LOG = logging.getLogger("ingestion")

def ensure_dirs():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def fetch_titanic(save_path="data/raw/titanic.csv"):
    """Descarga un dataset de ejemplo (Titanic) usando seaborn y lo guarda como CSV."""
    ensure_dirs()
    df = sns.load_dataset("titanic")
    df.to_csv(save_path, index=False)
    LOG.info("Dataset Titanic guardado en %s", save_path)
    return save_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetch_titanic()
