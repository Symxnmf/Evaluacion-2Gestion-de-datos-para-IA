from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "data/db/titanic.db")

def query_db(query):
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows

@app.route("/kpis")
def kpis():
    if not os.path.exists(DB_PATH):
        return jsonify({"error": "BD no encontrada. Ejecuta primero el pipeline."}), 404
    total = query_db("SELECT COUNT(*) FROM titanic")[0][0]
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
    exists = os.path.exists(DB_PATH)
    return jsonify({"bd_existe": exists})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
