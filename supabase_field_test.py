import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
if not url or not key:
    raise SystemExit('No env creds')
base = url.rstrip('/')
endpoint = base + '/titanic' if base.endswith('/rest/v1') else base + '/rest/v1/titanic'
headers = {'apikey': key, 'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

candidates = [
    'sobrevivio', 'sobrevivió', 'sobrevivio',
    'clase', 'categoria', 'categorias', 'categorías',
    'hermanos_cony', 'hermanos_conyuge', 'hermanos_conyuge',
    'tarifa', 'puerto_embarque', 'puerto_embarq', 'ciudad_puerto',
    'adulto_hombre', 'quien', 'solo_a'
]

for key in candidates:
    payload = [{key: 1}]
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
    print(key, resp.status_code, resp.text[:200])
