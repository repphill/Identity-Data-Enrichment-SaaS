import requests

def search_web(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers)
        return res.text
    except:
        return ""

def extract_links(html):
    links = []
    for part in html.split("href=\""):
        if "http" in part:
            link = part.split("\"")[0]
            links.append(link)
    return links

def find_social_links(links):
    socials = []

    for link in links:
        if "linkedin.com" in link:
            socials.append({"platform": "LinkedIn", "url": link})
        elif "twitter.com" in link:
            socials.append({"platform": "Twitter", "url": link})
        elif "facebook.com" in link:
            socials.append({"platform": "Facebook", "url": link})
        elif "instagram.com" in link:
            socials.append({"platform": "Instagram", "url": link})

    return socials

def find_youtube(links):
    yt = []
    for link in links:
        if "youtube.com" in link:
            yt.append(link)
    return yt

def enrich_email(email):
    domain = email.split("@")[-1]

    html = search_web(email)
    links = extract_links(html)

    socials = find_social_links(links)
    youtube = find_youtube(links)

    return {
        "email": email,
        "domain": domain,
        "social_profiles": socials[:5],
        "youtube_channels": youtube[:5],
        "confidence": "medium" if socials or youtube else "low"
    }
