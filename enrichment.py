import requests
import re

# =========================
# 🔍 SEARCH FUNCTION
# =========================
def search_web(query):
    url = f"https://duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.text
    except:
        return ""


# =========================
# 🔍 EXTRACT LINKS
# =========================
def extract_links(html):
    return re.findall(r'href="(https?://[^"]+)"', html)


# =========================
# 🧠 CLEAN LINKS
# =========================
def clean_links(links):
    clean = []
    for link in links:
        if "duckduckgo.com" in link:
            continue
        if "javascript" in link:
            continue
        clean.append(link)
    return list(set(clean))


# =========================
# 👤 USERNAME EXTRACTION
# =========================
def extract_username(email):
    return email.split("@")[0].lower()


# =========================
# 🧠 PERSONAL EMAIL DETECTION
# =========================
def is_personal_email(domain):
    personal_domains = [
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com",
        "icloud.com"
    ]
    return domain.lower() in personal_domains


# =========================
# 🔗 FIND SOCIAL LINKS
# =========================
def find_social_links(links, keyword):
    socials = []

    platforms = {
        "LinkedIn": "linkedin.com",
        "Twitter/X": "x.com",
        "Instagram": "instagram.com",
        "Facebook": "facebook.com"
    }

    for platform, domain in platforms.items():
        for link in links:
            if domain in link and keyword in link.lower():
                if "share" in link or "video" in link:
                    continue
                socials.append({
                    "platform": platform,
                    "url": link.split("?")[0]
                })
                break

    return socials


# =========================
# 📺 FIND YOUTUBE
# =========================
def find_youtube(links, keyword):
    results = []

    for link in links:
        if "youtube.com" in link and keyword in link.lower():
            if "watch" in link:
                continue
            results.append({
                "url": link.split("?")[0],
                "name": keyword.capitalize(),
                "subscribers": "Unknown"
            })

    return results[:1]


# =========================
# 🚀 MAIN FUNCTION
# =========================
def enrich_email(email):
    domain = email.split("@")[1]
    username = extract_username(email)

    # 🧠 DECIDE SEARCH TYPE
    if is_personal_email(domain):
        search_term = username
        company = username
    else:
        company = domain.split(".")[0]
        search_term = company

    # 🔍 SEARCH WEB
    html = ""
    html += search_web(f"{search_term} linkedin")
    html += search_web(f"{search_term} instagram")
    html += search_web(f"{search_term} twitter")
    html += search_web(f"{search_term} youtube")

    # 🔗 EXTRACT LINKS
    links = extract_links(html)
    links = clean_links(links)

    # 🔍 FIND SOCIALS
    socials = find_social_links(links, search_term)

    # 📺 YOUTUBE
    youtube = find_youtube(links, search_term)

    # 🎯 CONFIDENCE
    confidence = "high" if socials else "low"

    return {
        "email": email,
        "domain": domain,
        "company": company,
        "social_profiles": socials,
        "youtube_channels": youtube,
        "confidence": confidence
    }
