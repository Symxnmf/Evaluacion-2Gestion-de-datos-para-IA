from flask import Flask, jsonify
import os
import logging
from dotenv import load_dotenv
import requests

app = Flask(__name__)
load_dotenv()
# Prefer DATABASE_URL (Postgres) if present, else fall back to local sqlite path
DB_PATH = os.environ.get("DATABASE_URL") or os.environ.get("DB_PATH", os.environ.get("LOCAL_SQLITE_DB", "data/db/titanic.db"))
# Supabase REST config (read at startup)
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("app")


def query_db_sqlalchemy(query):
    """Run a SQL query using SQLAlchemy engine pointed at DATABASE_URL.

    Returns list of rows (tuples).
    """
    from sqlalchemy import create_engine, text
    # Normalize postgres URL if necessary
    url = DB_PATH
    if isinstance(url, str) and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text(query))
        return [tuple(r) for r in res.fetchall()]


def query_db_sqlite(query):
    import sqlite3
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows


def query_db_supabase():
    """Fetch all rows from Supabase REST for table `titanic` as list of dicts."""
    # Ensure .env is loaded in case process was started before .env changes
    load_dotenv()
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    if not supabase_url or not supabase_key:
        return None
    rest_base = supabase_url.rstrip('/')
    if rest_base.endswith('/rest/v1'):
        rest_endpoint = rest_base + '/titanic'
    else:
        rest_endpoint = rest_base + '/rest/v1/titanic'

    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Accept': 'application/json',
        'User-Agent': 'server-client/1.0'
    }
    try:
        LOG.info("Supabase URL: %s, key present: %s", supabase_url, bool(supabase_key))
        LOG.info("Consultando Supabase REST en %s", rest_endpoint + '?select=*')
        resp = requests.get(rest_endpoint + '?select=*', headers=headers, timeout=30)
        LOG.info("Respuesta Supabase: %s", getattr(resp, 'status_code', None))
    except Exception as e:
        LOG.exception("Error consultando Supabase: %s", e)
        return None
    if not resp.ok:
        LOG.error("Supabase REST error: %s %s", resp.status_code, resp.text)
        return None
    return resp.json()


def query_db(query):
    # If DB_PATH is a URL (starts with postgres:// or postgresql://), use SQLAlchemy
    if isinstance(DB_PATH, str) and DB_PATH.startswith("postgres"):
        try:
            return query_db_sqlalchemy(query)
        except Exception as e:
            LOG.exception("Error consultando la base remota: %s", e)
            return None
    # If Supabase REST is configured via environment, do not use SQL string queries here
    if os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_KEY'):
        LOG.debug("query_db called but Supabase REST is configured; use specific supabase functions instead.")
        return None
    return query_db_sqlite(query)

@app.route("/kpis")
def kpis():
    # If Supabase REST configured, fetch rows and compute KPIs in Python
    if os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_KEY'):
        rows = query_db_supabase()
        if not rows:
            return jsonify({"error": "BD no encontrada o error al consultar Supabase. Ejecuta primero el pipeline."}), 404
        total = len(rows)
        ages = [r.get('age') for r in rows if r.get('age') is not None]
        missing_age = sum(1 for r in rows if r.get('age') is None)
        avg_age = float(sum(ages) / len(ages)) if ages else None
        surv_vals = [r.get('survived') for r in rows if r.get('survived') is not None]
        # Convert possible string booleans or ints
        surv_nums = []
        for v in surv_vals:
            try:
                surv_nums.append(float(v))
            except Exception:
                try:
                    surv_nums.append(1.0 if str(v).lower() in ('true', '1') else 0.0)
                except Exception:
                    pass
        survival_rate = float(sum(surv_nums) / total) if total > 0 else None
        return jsonify({
            "filas_totales": total,
            "edad_faltante": missing_age,
            "edad_promedio": avg_age,
            "tasa_supervivencia": survival_rate
        })

    # Fallback to SQL queries (SQLite or SQLAlchemy)
    rows = query_db("SELECT COUNT(*) FROM titanic")
    if not rows:
        return jsonify({"error": "BD no encontrada o error al consultar. Ejecuta primero el pipeline."}), 404
    total = rows[0][0]
    missing_age = query_db("SELECT SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) FROM titanic")[0][0]
    avg_age = query_db("SELECT AVG(age) FROM titanic")[0][0]
    survival_rate = query_db("SELECT AVG(survived) FROM titanic")[0][0]
    return jsonify({
        "filas_totales": total,
        "edad_faltante": missing_age,
        "edad_promedio": avg_age,
        "tasa_supervivencia": survival_rate
    })

@app.route("/status")
def status():
    # Report availability depending on configured backend
    if os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_KEY'):
        # simple health check on Supabase table
        rows = query_db_supabase()
        return jsonify({"bd_existe": bool(rows)})
    exists = os.path.exists(DB_PATH)
    return jsonify({"bd_existe": exists})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
