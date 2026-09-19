import sqlite3
import json
import os
import time
import requests
import hashlib

CACHE_DB = os.path.join(os.path.dirname(__file__), "cache", "api_cache.db")
os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)

def get_db():
    conn = sqlite3.connect(CACHE_DB)
    conn.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, response TEXT, timestamp REAL)")
    return conn

with get_db() as conn:
    pass

last_call_time = 0

def fetch(url, params=None, method="GET", json_data=None, provider="default"):
    global last_call_time
    
    cache_params = {}
    if params:
        cache_params = {k: v for k, v in params.items() if k.lower() != "apikey"}
        
    key_dict = {
        "provider": provider,
        "url": url,
        "method": method,
        "params": cache_params,
        "json_data": json_data
    }
    key_str = json.dumps(key_dict, sort_keys=True)
    key_hash = hashlib.sha256(key_str.encode()).hexdigest()
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT response FROM cache WHERE key = ?", (key_hash,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
            
    elapsed = time.time() - last_call_time
    if elapsed < 0.25:
        time.sleep(0.25 - elapsed)
        
    max_retries = 3
    for attempt in range(max_retries):
        try:
            last_call_time = time.time()
            if method == "GET":
                resp = requests.get(url, params=params, timeout=10)
            else:
                resp = requests.post(url, json=json_data, timeout=10)
                
            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                
            resp.raise_for_status()
            data = resp.json()
            
            with get_db() as conn:
                conn.execute("INSERT OR REPLACE INTO cache (key, response, timestamp) VALUES (?, ?, ?)",
                             (key_hash, json.dumps(data), time.time()))
            return data
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            print(f"Error fetching {url}: {e}")
            return None
