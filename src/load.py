import os
import logging
import pandas as pd
import numpy as np
from dotenv import load_dotenv

LOG = logging.getLogger("load")


def ensure_dirs():
    # Asegurar carpeta para base de datos local
    os.makedirs("data/db", exist_ok=True)


def load_to_database(processed_path="data/processed/titanic_clean.csv"):
    """Carga el CSV procesado en la base configurada por variables de entorno.

    Flujo:
    - Si `DATABASE_URL` está definido, subir a Postgres vía SQLAlchemy.
    - Si no, pero existen `SUPABASE_URL` y `SUPABASE_KEY`, usar REST API de Supabase.
    - Si ninguna está presente, almacenar en SQLite local `data/db/titanic.db`.
    """
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")

    # Leer CSV procesado
    df = pd.read_csv(processed_path)

    # Opción 1: subir a Postgres remoto usando SQLAlchemy
    if db_url:
        try:
            from sqlalchemy import create_engine
        except Exception as exc:
            LOG.exception("SQLAlchemy no está disponible: %s", exc)
            raise

        # Normalizar URL si el proveedor devuelve 'postgres://'
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)

        LOG.info("Conectando a la base remota via DATABASE_URL")
        engine = create_engine(db_url)
        # Escribir tabla 'titanic' (reemplaza si existe)
        df.to_sql("titanic", engine, if_exists="replace", index=False)
        LOG.info("Datos cargados en la base remota (tabla: titanic)")
        return db_url

    # Opción 2: si están credenciales de Supabase, usar su REST para insertar filas
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_url and supabase_key:
        try:
            import requests
        except Exception as exc:
            LOG.exception("Requests no está disponible: %s", exc)
            raise

        # Construir endpoint REST para la tabla 'titanic'
        rest_base = supabase_url.rstrip('/')
        if rest_base.endswith('/rest/v1'):
            rest_endpoint = rest_base + '/titanic'
        else:
            rest_endpoint = rest_base + '/rest/v1/titanic'

        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates'
        }

        LOG.info("Subiendo %d filas a Supabase REST %s", len(df), rest_endpoint)

        # Mapear nombres de columnas a los nombres en la tabla de Supabase (español)
        column_mapping = {
            'survived': 'sobrevivio',
            'pclass': 'clase',
            'sex': 'sexo',
            'age': 'edad',
            'sibsp': 'hermanos_conyuge',
            'parch': 'padres_hijos',
            'fare': 'tarifa',
            'embarked': 'puerto_embarque',
            'who': 'quien',
            'adult_male': 'adulto_hombre',
            'embark_town': 'ciudad_puerto',
            'alone': 'solo_a',
            'class': 'categoria'
        }

        df_renamed = df.rename(columns=column_mapping)

        # Preparar registros: reemplazar NaN/inf por None y convertir tipos numpy
        df_clean = df_renamed.replace([np.nan, np.inf, -np.inf], None)
        records_raw = df_clean.to_dict(orient='records')

        def _convert_record(rec):
            # Convertir tipos numpy a tipos nativos de Python para JSON
            new = {}
            for k, v in rec.items():
                if isinstance(v, (np.integer, np.int64, np.int32)):
                    new[k] = int(v)
                elif isinstance(v, (np.floating, np.float64, np.float32)):
                    new[k] = None if v is None else float(v)
                elif isinstance(v, (np.bool_)):
                    new[k] = bool(v)
                else:
                    new[k] = v
            return new

        records = [_convert_record(r) for r in records_raw]
        chunk_size = 500
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i+chunk_size]
            resp = requests.post(rest_endpoint, json=chunk, headers=headers)
            if not resp.ok:
                LOG.error("Error subiendo chunk %d-%d: %s %s", i, i+len(chunk), resp.status_code, resp.text)
                raise RuntimeError(f"Failed to upload to Supabase REST: {resp.status_code} {resp.text}")

        LOG.info("Datos cargados via Supabase REST en tabla 'titanic'")
        return rest_endpoint
    else:
        # Opción 3: fallback a SQLite local
        ensure_dirs()
        db_path = os.getenv("LOCAL_SQLITE_DB", "data/db/titanic.db")
        import sqlite3

        conn = sqlite3.connect(db_path)
        df.to_sql("titanic", conn, if_exists="replace", index=False)
        conn.close()
        LOG.info("DATABASE_URL no encontrada — datos cargados en SQLite local: %s", db_path)
        return db_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_to_database()
