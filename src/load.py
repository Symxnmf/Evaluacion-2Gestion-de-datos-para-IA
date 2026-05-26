import os
import logging
import pandas as pd
import numpy as np
from dotenv import load_dotenv

LOG = logging.getLogger("load")


def ensure_dirs():
    os.makedirs("data/db", exist_ok=True)


def load_to_database(processed_path="data/processed/titanic_clean.csv"):
    """Carga `processed_path` a la base indicada por `DATABASE_URL`.

    Comportamiento:
    - Si existe `DATABASE_URL` en el entorno, usa SQLAlchemy/psycopg2 para subir a Postgres.
    - Si no existe, hace fallback a SQLite local en `data/db/titanic.db`.
    """
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")

    df = pd.read_csv(processed_path)

    if db_url:
        try:
            from sqlalchemy import create_engine
        except Exception as exc:
            LOG.exception("SQLAlchemy no está disponible: %s", exc)
            raise

        # Normalize postgres URL for SQLAlchemy (some providers use postgres://)
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)

        LOG.info("Conectando a la base remota via DATABASE_URL")
        engine = create_engine(db_url)
        # write dataframe to SQL (will create/replace table)
        df.to_sql("titanic", engine, if_exists="replace", index=False)
        LOG.info("Datos cargados en la base remota (tabla: titanic)")
        return db_url
    # If DATABASE_URL not set, but SUPABASE REST credentials exist, use REST API
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_url and supabase_key:
        try:
            import requests
        except Exception as exc:
            LOG.exception("Requests no está disponible: %s", exc)
            raise

        # Build REST endpoint for table 'titanic'
        rest_base = supabase_url.rstrip('/')
        # Supabase REST endpoints usually under /rest/v1
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

        # Post in chunks to avoid huge payloads
        # Replace NaN/inf with None and convert numpy types to native Python types
        df_clean = df.replace([np.nan, np.inf, -np.inf], None)
        records_raw = df_clean.to_dict(orient='records')

        def _convert_record(rec):
            new = {}
            for k, v in rec.items():
                # convert numpy scalar types to native python
                if isinstance(v, (np.integer, np.int64, np.int32)):
                    new[k] = int(v)
                elif isinstance(v, (np.floating, np.float64, np.float32)):
                    # None will remain None, floats are converted to Python float
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
        # Fallback a sqlite local
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
