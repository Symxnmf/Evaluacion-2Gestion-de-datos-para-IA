import pandas as pd
import logging

LOG = logging.getLogger("validation")

REQUIRED_COLUMNS = ["survived", "pclass", "sex", "age", "sibsp", "parch", "fare"]

def validate_schema(path="data/processed/titanic_clean.csv"):
    df = pd.read_csv(path)
    miss = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if miss:
        LOG.error("Faltan columnas requeridas: %s", miss)
        raise ValueError(f"Faltan columnas: {miss}")
    # Comprobaciones semánticas simples
    if (df["age"] < 0).any():
        LOG.error("Se encontraron edades negativas")
        raise ValueError("Se encontraron edades negativas")
    if not df["survived"].isin([0,1]).all():
        LOG.error("Valores inválidos en la columna 'survived'")
        raise ValueError("Valores inválidos en 'survived'")
    LOG.info("Validación satisfactoria para %s", path)
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    validate_schema()
