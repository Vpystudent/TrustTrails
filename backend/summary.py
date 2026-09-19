import os
import json
import hashlib
from openai import OpenAI
from backend.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from backend.cache import fetch

def write_summary(signals):
    if not signals:
        return "No risk signals found for this address. It appears to be safe based on the checks performed."
        
    # cache by hash
    sig_str = json.dumps(signals, sort_keys=True)
    h = hashlib.sha256(sig_str.encode()).hexdigest()
    
    # Simple file-based cache for summaries
    cache_dir = os.path.join(os.path.dirname(__file__), 'cache', 'summaries')
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{h}.txt")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return f.read()
            
    fallback = f"This address has {len(signals)} risk finding(s), including: {signals[0]['title']}. Please proceed with caution and verify the evidence."
    
    try:
        if not LLM_API_KEY:
            return fallback
            
        client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL
        )
        
        system_prompt = "You explain blockchain risk findings to non-technical people. Use ONLY the findings provided. Do not invent facts. Do not give a score or verdict. Write 3-5 short sentences, mention the most serious finding first, and end with one safe next step."
        
        # Prepare findings text
        findings_text = ""
        for i, s in enumerate(signals):
            findings_text += f"{i+1}. {s['title']} ({s['severity']} severity): {s['rule']}\n"
            
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Findings:\n{findings_text}"}
            ],
            timeout=15
        )
        summary = response.choices[0].message.content.strip()
        
        with open(cache_file, 'w') as f:
            f.write(summary)
            
        return summary
    except Exception as e:
        print(f"LLM Error: {e}")
        return fallback
