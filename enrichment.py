import requests
import re

# 🔍 Search using DuckDuckGo (scrapable)
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


# 🔗 Extract links from HTML
def extract_links(html):
    links = re.findall(r'href="(https?://[^"]+)"', html)
    return links


# 🌐 Find social profiles
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


# 🎥 Find YouTube channels
def find_youtube(links):
    yt = []

    for link in links:
        if "youtube.com" in link:
            yt.append(link)

    return yt


# 🧠 Main enrichment function
def enrich_email(email):
    domain = email.split("@")[-1]

    # 🔍 Multiple smart searches
    html = ""
    html += search_web(f'"{email}"')
    html += search_web(f'{domain} social media')
    html += search_web(f'{domain} youtube')
    html += search_web(f'{domain} linkedin')

    links = extract_links(html)

    socials = find_social_links(links)
    youtube = find_youtube(links)

    # 🧠 Confidence logic
    if socials or youtube:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "email": email,
        "domain": domain,
        "social_profiles": socials[:5],
        "youtube_channels": youtube[:5],
        "confidence": confidence
    }
