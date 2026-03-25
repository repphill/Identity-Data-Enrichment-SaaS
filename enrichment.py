import hashlib
import requests

def gravatar_lookup(email):
    hash_email = hashlib.md5(email.lower().encode()).hexdigest()
    url = f"https://www.gravatar.com/{hash_email}.json"

    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
    except:
        pass

    return None

def enrich_email(email):
    domain = email.split("@")[-1]

    return {
        "email": email,
        "domain": domain,
        "confidence": "low"
    }