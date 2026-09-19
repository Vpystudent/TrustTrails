import os
import json
import sqlite3
import hashlib
import time
from backend.config import get_env
import openai

SUMMARY_DB = os.path.join(os.path.dirname(__file__), "cache", "summary_cache.db")
os.makedirs(os.path.dirname(SUMMARY_DB), exist_ok=True)

def get_db():
    conn = sqlite3.connect(SUMMARY_DB)
    conn.execute("CREATE TABLE IF NOT EXISTS summary_cache (hash TEXT PRIMARY KEY, summary TEXT, status TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS usage (date TEXT PRIMARY KEY, count INTEGER)")
    return conn

with get_db() as conn:
    pass

def generate_fallback(findings):
    if not findings:
        return "No risk signals found by these checks. Not a guarantee of safety. New or low-activity addresses can look clean."
    
    parts = []
    for f in sorted(findings, key=lambda x: -x.get('score', 0))[:3]:
        pts = int(f.get('score', 0) * 100) # Roughly
        ev_count = len(f.get('evidence', []))
        parts.append(f"{f['title']}. {ev_count} piece(s) of evidence found.")
        
    return " ".join(parts) + " Review the evidence below."

def write_summary(findings):
    env_mode = get_env("AI_SUMMARY", "auto").lower()
    
    findings_str = json.dumps(findings, sort_keys=True)
    findings_hash = hashlib.sha256(findings_str.encode()).hexdigest()
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT summary, status FROM summary_cache WHERE hash = ?", (findings_hash,))
        row = cur.fetchone()
        if row:
            return {"summary": row[0], "status": row[1]}
            
    if env_mode == "off":
        fallback = generate_fallback(findings)
        return {"summary": fallback, "status": "disabled"}
        
    today = time.strftime("%Y-%m-%d")
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT count FROM usage WHERE date = ?", (today,))
        row = cur.fetchone()
        count = row[0] if row else 0
        
        if count >= int(get_env("AI_SUMMARY_BUDGET", "15")):
            fallback = generate_fallback(findings)
            return {"summary": fallback, "status": "quota"}
            
    if not findings:
        return {"summary": "No risk signals found by these checks. Not a guarantee of safety. New or low-activity addresses can look clean.", "status": "ok"}
        
    api_key = get_env("LLM_API_KEY", "")
    if not api_key:
        fallback = generate_fallback(findings)
        return {"summary": fallback, "status": "disabled"}
        
    client = openai.OpenAI(api_key=api_key, base_url=get_env("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"))
    model = get_env("LLM_MODEL", "gemini-3.8-flash")
    fallback_model = get_env("LLM_FALLBACK_MODEL", "")
    
    prompt = f"Summarize these findings in 2 short sentences. Neutral tone. Do not use the words safe, clean, or perfect: {json.dumps(findings)}"
    
    summary = ""
    status = "ok"
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        summary = resp.choices[0].message.content
        
        with get_db() as conn:
            conn.execute("INSERT OR REPLACE INTO usage (date, count) VALUES (?, ?)", (today, count + 1))
            
    except Exception as e:
        print(f"Summary LLM error: {e}")
        is_429 = "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
        if is_429 and fallback_model:
            try:
                resp = client.chat.completions.create(
                    model=fallback_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100
                )
                summary = resp.choices[0].message.content
                with get_db() as conn:
                    conn.execute("INSERT OR REPLACE INTO usage (date, count) VALUES (?, ?)", (today, count + 1))
            except Exception as e2:
                print(f"Fallback LLM error: {e2}")
                summary = generate_fallback(findings)
                status = "quota" if is_429 else "fallback"
        else:
            summary = generate_fallback(findings)
            status = "quota" if is_429 else "fallback"
            
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO summary_cache (hash, summary, status) VALUES (?, ?, ?)",
                     (findings_hash, summary, status))
                     
    return {"summary": summary, "status": status}
