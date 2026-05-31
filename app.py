from flask import Flask, jsonify, render_template_string, request
import os
import logging
from dotenv import load_dotenv
import requests

app = Flask(__name__)
load_dotenv()
# Selección de la base de datos:
# - Si está definida `DATABASE_URL`, se usa como URL remota (Postgres).
# - En caso contrario, se toma `DB_PATH` o `LOCAL_SQLITE_DB` y se usa SQLite local.
DB_PATH = os.environ.get("DATABASE_URL") or os.environ.get("DB_PATH", os.environ.get("LOCAL_SQLITE_DB", "data/db/titanic.db"))
# Configuración opcional para Supabase (REST). Si están definidas, la app
# puede consultar/insertar directamente vía REST.
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("app")


def query_db_sqlalchemy(query):
    """Ejecuta una consulta SQL usando SQLAlchemy apuntando a `DB_PATH`.

    Retorna una lista de filas (tuplas).
    """
    from sqlalchemy import create_engine, text
    # Normalizar URL de Postgres si el proveedor devuelve 'postgres://'
    url = DB_PATH
    if isinstance(url, str) and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    # Crear engine y ejecutar la consulta
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text(query))
        return [tuple(r) for r in res.fetchall()]


def query_db_sqlite(query):
    # Ejecuta una consulta directa en SQLite local (archivo en `DB_PATH`).
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
    """Consulta la tabla `titanic` vía Supabase REST y retorna lista de dicts.

    Retorna `None` si no hay configuración o si ocurre un error.
    """
    # Asegurar que las variables de entorno estén cargadas
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
    # Si `DB_PATH` apunta a Postgres, usar SQLAlchemy
    if isinstance(DB_PATH, str) and DB_PATH.startswith("postgres"):
        try:
            return query_db_sqlalchemy(query)
        except Exception as e:
            LOG.exception("Error consultando la base remota: %s", e)
            return None
    # Si Supabase REST está configurado, las consultas SQL directas no se usan
    if os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_KEY'):
        LOG.debug("Supabase REST configurado: evitar consultas SQL directas desde aquí.")
        return None
    # Fallback a SQLite local
    return query_db_sqlite(query)

@app.route("/kpis")
def kpis():
    # Si Supabase REST está configurado, obtener filas vía REST y calcular KPIs en Python
    if os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_KEY'):
        rows = query_db_supabase()
        if not rows:
            return jsonify({"error": "BD no encontrada o error al consultar Supabase. Ejecuta primero el pipeline."}), 404
        total = len(rows)
        ages = [r.get('age') for r in rows if r.get('age') is not None]
        missing_age = sum(1 for r in rows if r.get('age') is None)
        avg_age = float(sum(ages) / len(ages)) if ages else None
        surv_vals = [r.get('survived') for r in rows if r.get('survived') is not None]
        # Normalizar valores de supervivencia (pueden venir como '1','0','true','false')
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

    # Si no hay Supabase, usar consultas SQL (SQLite o Postgres vía SQLAlchemy)
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

@app.route("/")
def index():
    # HTML embebido: formulario envía POST a `/insert` y enlaces a `/kpis` y `/status`
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Demo Titanic DataOps</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            h1 { color: #333; }
            .section { margin-bottom: 40px; }
            form { background: #f9f9f9; padding: 20px; border-radius: 5px; }
            .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
            label { display: block; margin-top: 10px; font-weight: bold; color: #333; }
            input, select, textarea { width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin-top: 15px; font-size: 16px; }
            button:hover { background: #0056b3; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .links { margin-top: 20px; }
            .links a { display: inline-block; margin-right: 20px; padding: 10px 15px; background: #f0f0f0; border-radius: 4px; }
            .links a:hover { background: #e0e0e0; text-decoration: none; }
            .success { color: green; margin-top: 10px; }
            .error { color: red; margin-top: 10px; }
            .info { background: #e7f3ff; padding: 10px; border-left: 4px solid #007bff; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚢 Demo Titanic DataOps</h1>
            
            <div class="section">
                <h2>Agregar nuevo pasajero</h2>
                <div class="info">Completa el formulario con los datos del pasajero. Todos los campos son requeridos.</div>
                <form method="POST" action="/insert">
                    <div class="form-grid">
                        <div>
                            <label>¿Sobrevivió? *</label>
                            <select name="survived" required>
                                <option value="">Selecciona...</option>
                                <option value="0">❌ No sobrevivió</option>
                                <option value="1">✓ Sobrevivió</option>
                            </select>
                        </div>
                        
                        <div>
                            <label>Clase de pasaje *</label>
                            <select name="pclass" required>
                                <option value="">Selecciona...</option>
                                <option value="1">🥇 Primera clase</option>
                                <option value="2">🥈 Segunda clase</option>
                                <option value="3">🥉 Tercera clase</option>
                            </select>
                        </div>
                        
                        <div>
                            <label>Sexo *</label>
                            <select name="sex" required>
                                <option value="">Selecciona...</option>
                                <option value="0">Hombre</option>
                                <option value="1">Mujer</option>
                            </select>
                        </div>
                        
                        <div>
                            <label>Edad (años) *</label>
                            <input type="number" name="age" step="0.1" min="0" max="120" required>
                        </div>
                        
                        <div>
                            <label>Hermanos/Cónyuge a bordo *</label>
                            <input type="number" name="sibsp" min="0" value="0" required>
                        </div>
                        
                        <div>
                            <label>Padres/Hijos a bordo *</label>
                            <input type="number" name="parch" min="0" value="0" required>
                        </div>
                        
                        <div>
                            <label>Tarifa (precio del boleto) *</label>
                            <input type="number" name="fare" step="0.01" min="0" required>
                        </div>
                        
                        <div>
                            <label>Puerto de embarque *</label>
                            <select name="embarked" required>
                                <option value="">Selecciona...</option>
                                <option value="S">Southampton (S)</option>
                                <option value="C">Cherbourg (C)</option>
                                <option value="Q">Queenstown (Q)</option>
                            </select>
                        </div>
                        
                        <div>
                            <label>Categoría de pasajero *</label>
                            <select name="who" required>
                                <option value="">Selecciona...</option>
                                <option value="man">Hombre adulto</option>
                                <option value="woman">Mujer adulta</option>
                                <option value="child">Niño/a</option>
                            </select>
                        </div>
                        
                        <div>
                            <label>¿Viajaba solo/a? *</label>
                            <select name="alone" required>
                                <option value="">Selecciona...</option>
                                <option value="True">Sí, viajaba solo/a</option>
                                <option value="False">No, viajaba con familia</option>
                            </select>
                        </div>
                        
                        <div>
                            <label>Puerto de desembarque</label>
                            <input type="text" name="embark_town" placeholder="ej: Southampton">
                        </div>
                    </div>
                    
                    <button type="submit">💾 Guardar en Supabase</button>
                </form>
                <div id="message"></div>
            </div>
            
            <div class="section">
                <h2>📊 Acceso a datos</h2>
                <div class="links">
                    <a href="/kpis">📈 Ver KPIs y estadísticas</a>
                    <a href="/status">🔍 Ver estado de la base</a>
                </div>
            </div>
        </div>
        
        <script>
            document.querySelector('form').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const response = await fetch('/insert', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                const messageDiv = document.getElementById('message');
                if (response.ok) {
                    messageDiv.innerHTML = '<div class="success">✓ Registro guardado exitosamente</div>';
                    this.reset();
                } else {
                    messageDiv.innerHTML = '<div class="error">❌ Error: ' + data.error + '</div>';
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/insert", methods=["POST"])
def insert():
    try:
        # Esta ruta inserta un nuevo registro en Supabase REST.
        if not SUPABASE_URL or not SUPABASE_KEY:
            return jsonify({"error": "Supabase no configurado"}), 400
        
        # Recopilar datos del formulario con nombres en español y derivar campos faltantes
        pclass_value = request.form.get("pclass")
        pclass_num = int(pclass_value) if pclass_value and pclass_value.isdigit() else None
        categoria_label = {
            1: "Primero",
            2: "Segundo",
            3: "Tercero"
        }.get(pclass_num)

        sex_value = request.form.get("sex")
        who_value = request.form.get("who")

        # Construir el registro en el esquema que espera la tabla en Supabase
        record = {
            "sobrevivio": int(request.form.get("survived")),
            "clase": pclass_num,
            "sexo": int(sex_value) if sex_value is not None else None,
            "edad": float(request.form.get("age")),
            "hermanos_conyuge": int(request.form.get("sibsp")),
            "padres_hijos": int(request.form.get("parch")),
            "tarifa": float(request.form.get("fare")),
            "puerto_embarque": request.form.get("embarked", ""),
            "categoria": categoria_label,
            "quien": who_value or "",
            "adulto_hombre": sex_value == "0" and who_value == "man",
            "solo_a": request.form.get("alone") == "True",
            "ciudad_puerto": request.form.get("embark_town", "")
        }
        
        rest_base = SUPABASE_URL.rstrip('/')
        if rest_base.endswith('/rest/v1'):
            rest_endpoint = rest_base + '/titanic'
        else:
            rest_endpoint = rest_base + '/rest/v1/titanic'
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        
        # Enviar un arreglo con un solo registro al endpoint REST de Supabase
        resp = requests.post(rest_endpoint, json=[record], headers=headers, timeout=10)
        
        if not resp.ok:
            LOG.error("Error insertando en Supabase: %s", resp.text)
            return jsonify({"error": f"Supabase error: {resp.status_code}"}), resp.status_code
        
        LOG.info("Registro insertado: %s", record)
        return jsonify({"success": "Registro guardado en Supabase"}), 201
    
    except Exception as e:
        LOG.exception("Error en /insert: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/status")
def status():
    # Report availability depending on configured backend
    # Reportar disponibilidad según backend configurado
    if os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_KEY'):
        rows = query_db_supabase()
        return jsonify({"bd_existe": bool(rows)})
    exists = os.path.exists(DB_PATH)
    return jsonify({"bd_existe": exists})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
