import os
from dotenv import load_dotenv
import requests
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
print('SUPABASE_URL', SUPABASE_URL)
print('KEY present', bool(SUPABASE_KEY))
rest_base = SUPABASE_URL.rstrip('/')
if rest_base.endswith('/rest/v1'):
    rest_endpoint = rest_base + '/titanic'
else:
    rest_endpoint = rest_base + '/rest/v1/titanic'
headers = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Accept': 'application/json', 'User-Agent': 'server-client/1.0'}
resp = requests.get(rest_endpoint + '?select=*', headers=headers, timeout=15)
print('status', resp.status_code)
print(resp.text[:500])
