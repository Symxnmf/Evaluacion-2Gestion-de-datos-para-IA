import os
import subprocess
import sqlite3

def test_pipeline_runs():
    # Run pipeline
    p = subprocess.run(["python", "-m", "src.pipeline"], check=False)
    assert p.returncode == 0
    # Check sqlite created
    db = "data/db/titanic.db"
    assert os.path.exists(db)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM titanic")
    cnt = cur.fetchone()[0]
    conn.close()
    assert cnt > 0
