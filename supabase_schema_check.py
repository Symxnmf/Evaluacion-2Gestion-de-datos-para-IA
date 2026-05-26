import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
print('SUPABASE_URL', bool(url))
print('SUPABASE_KEY', bool(key))
if not url or not key:
    raise SystemExit('No env creds')

base = url.rstrip('/')
endpoint = base + '/titanic' if base.endswith('/rest/v1') else base + '/rest/v1/titanic'
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Accept': 'application/json'
}
resp = requests.get(endpoint + '?select=*', headers=headers, timeout=30)
print('status', resp.status_code)
print(resp.text[:2000])
