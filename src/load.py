import sqlite3
import pandas as pd
import os
import logging

LOG = logging.getLogger("load")

def ensure_dirs():
    os.makedirs("data/db", exist_ok=True)

def load_to_sqlite(processed_path="data/processed/titanic_clean.csv", db_path="data/db/titanic.db"):
    ensure_dirs()
    df = pd.read_csv(processed_path)
    conn = sqlite3.connect(db_path)
    df.to_sql("titanic", conn, if_exists="replace", index=False)
    conn.close()
    LOG.info("Datos cargados en la base SQLite en %s", db_path)
    return db_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_to_sqlite()
