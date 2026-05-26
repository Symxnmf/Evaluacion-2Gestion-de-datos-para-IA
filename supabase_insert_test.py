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
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
}

payload = [{
    'sobrevivio': 1,
    'clase': 1,
    'sexo': 0,
    'edad': 30,
    'hermanos_conyuge': 0,
    'padres_hijos': 0,
    'tarifa': 100.0,
    'puerto_embarque': 'S',
    'categoria': 'Primero',
    'quien': 'man',
    'adulto_hombre': True,
    'ciudad_puerto': 'Southampton',
    'solo_a': True,
}]

resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
print('status', resp.status_code)
print(resp.text)
