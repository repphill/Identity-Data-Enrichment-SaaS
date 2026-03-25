import requests
from urllib.parse import unquote


# 🔍 DuckDuckGo search (reliable)
def search_web(query):
    url = "https://duckduckgo.com/html/"
    params = {"q": query}

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.post(url, data=params, headers=headers)
        return res.text
    except:
        return ""


# 🔗 Extract real links (FIXED — decodes DuckDuckGo redirects)
def extract_links(html):
    links = []

    parts = html.split("uddg=")

    for part in parts[1:]:
        url = part.split("&")[0]
        decoded = unquote(url)

        if decoded.startswith("http"):
            links.append(decoded)

    return links


# 🌐 Detect social platforms
def find_social_links(links):
    socials = []

    for link in links:
        if "linkedin.com" in link:
            socials.append({"platform": "LinkedIn", "url": link})
        elif "twitter.com" in link or "x.com" in link:
            socials.append({"platform": "Twitter/X", "url": link})
        elif "facebook.com" in link:
            socials.append({"platform": "Facebook", "url": link})
        elif "instagram.com" in link:
            socials.append({"platform": "Instagram", "url": link})

    return socials


# 🎥 Detect YouTube links
def find_youtube(links):
    yt = []

    for link in links:
        if "youtube.com" in link:
            yt.append(link)

    return yt


# 🧠 MAIN ENRICHMENT FUNCTION
def enrich_email(email):
    domain = email.split("@")[-1]
    company = domain.replace(".com", "")

    html = ""

    # 🔥 Stronger company-based searches
    html += search_web(f"{company} official website")
    html += search_web(f"{company} linkedin")
    html += search_web(f"{company} twitter")
    html += search_web(f"{company} facebook")
    html += search_web(f"{company} youtube")

    # Extract links
    links = extract_links(html)

    # Find data
    socials = find_social_links(links)
    youtube = find_youtube(links)

    # Remove duplicates
    socials = list({s['url']: s for s in socials}.values())
    youtube = list(set(youtube))

    # Confidence logic
    if socials or youtube:
        confidence = "high"
    else:
        confidence = "low"

    return {
        "email": email,
        "domain": domain,
        "company": company,
        "social_profiles": socials[:5],
        "youtube_channels": youtube[:5],
        "confidence": confidence
    }
