import pandas as pd
import os
import logging

LOG = logging.getLogger("processing")

def ensure_dirs():
    os.makedirs("data/processed", exist_ok=True)

def clean_transform(raw_path="data/raw/titanic.csv", out_path="data/processed/titanic_clean.csv"):
    ensure_dirs()
    df = pd.read_csv(raw_path)
    # Pasos simples de limpieza
    # Rellenar 'age' con la mediana
    if "age" in df.columns:
        df["age"] = df["age"].fillna(df["age"].median())
    # Rellenar 'embark_town' con la moda
    if "embark_town" in df.columns:
        df["embark_town"] = df["embark_town"].fillna(df["embark_town"].mode().iloc[0])
    # Codificar 'sex'
    if "sex" in df.columns:
        df["sex"] = df["sex"].map({"male": 0, "female": 1})
    # Eliminar columnas irrelevantes o con muchos nulos
    for col in ["deck", "alive"]:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
    df.to_csv(out_path, index=False)
    LOG.info("Datos procesados guardados en %s", out_path)
    return out_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    clean_transform()
