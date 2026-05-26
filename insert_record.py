from dotenv import load_dotenv
import os, requests, json

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit("SUPABASE_URL or SUPABASE_KEY not set in environment (.env)")

rest_base = SUPABASE_URL.rstrip('/')
rest_endpoint = rest_base + '/titanic' if rest_base.endswith('/rest/v1') else rest_base + '/rest/v1/titanic'

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'User-Agent': 'server-client/1.0',
    # Prefer merge-duplicates to perform upsert when primary key exists
    'Prefer': 'resolution=merge-duplicates'
}

# Example payload - change id if needed
payload = [{
    "id": 1001,
    "survived": 1,
    "pclass": 1,
    "sex": 1,
    "age": 30,
    "sibsp": 0,
    "parch": 0,
    "fare": 50.0,
    "embarked": "S"
}]

print("Posting to", rest_endpoint)
r = requests.post(rest_endpoint, json=payload, headers=headers, timeout=30)
print(r.status_code)
print(r.text)
