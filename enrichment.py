import requests
import re

# =========================
# 🔍 SEARCH
# =========================
def search_web(query):
    url = f"https://duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        return requests.get(url, headers=headers, timeout=10).text
    except:
        return ""


# =========================
# 🔗 EXTRACT LINKS
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
        clean.append(link.split("?")[0])
    return list(set(clean))


# =========================
# 👤 USERNAME
# =========================
def extract_username(email):
    return email.split("@")[0].lower()


# =========================
# 🧠 PERSONAL EMAIL CHECK
# =========================
def is_personal_email(domain):
    return domain.lower() in [
        "gmail.com", "yahoo.com", "hotmail.com",
        "outlook.com", "icloud.com"
    ]


# =========================
# 🔄 USERNAME VARIATIONS
# =========================
def username_variations(username):
    return list(set([
        username,
        username.replace(".", ""),
        username.replace("_", ""),
        username.replace(".", "_"),
        username.replace("_", "."),
    ]))


# =========================
# 🧠 SCORING
# =========================
def score_link(link, variations):
    score = 0
    link_lower = link.lower()

    for v in variations:
        if v in link_lower:
            score += 10

    # bonus for profile-like URLs
    if "/in/" in link or "/@" in link:
        score += 5

    # penalty for junk
    if "video" in link or "share" in link:
        score -= 5

    return max(score, 0)


# =========================
# 🔗 FIND SOCIALS
# =========================
def find_social_links(links, username):
    socials = []

    platforms = {
        "LinkedIn": "linkedin.com",
        "Twitter/X": "x.com",
        "Instagram": "instagram.com",
        "Facebook": "facebook.com"
    }

    variations = username_variations(username)

    for platform, domain in platforms.items():
        scored = []

        for link in links:
            if domain in link:
                s = score_link(link, variations)
                if s > 0:
                    scored.append((link, s))

        scored.sort(key=lambda x: x[1], reverse=True)

        if scored:
            best_link, best_score = scored[0]
            socials.append({
                "platform": platform,
                "url": best_link,
                "score": best_score
            })

    return socials


# =========================
# 📺 YOUTUBE
# =========================
def find_youtube(links, username):
    variations = username_variations(username)
    scored = []

    for link in links:
        if "youtube.com" in link and "watch" not in link:
            s = score_link(link, variations)
            if s > 0:
                scored.append((link, s))

    scored.sort(key=lambda x: x[1], reverse=True)

    if scored:
        best_link, best_score = scored[0]
        return [{
            "url": best_link,
            "name": username.capitalize(),
            "subscribers": "Unknown",
            "score": best_score
        }]

    return []


# =========================
# 🎯 FINAL CONFIDENCE
# =========================
def calculate_confidence(total_score):
    if total_score >= 40:
        return "high"
    elif total_score >= 20:
        return "medium"
    else:
        return "low"


# =========================
# 🚀 MAIN FUNCTION
# =========================
def enrich_email(email):
    domain = email.split("@")[1]
    username = extract_username(email)

    # decide mode
    if is_personal_email(domain):
        search_terms = username_variations(username)
        company = username
    else:
        company = domain.split(".")[0]
        search_terms = [company]

    html = ""

    for term in search_terms:
        html += search_web(f"{term} linkedin")
        html += search_web(f"{term} instagram")
        html += search_web(f"{term} twitter")
        html += search_web(f"{term} youtube")

    links = clean_links(extract_links(html))

    socials = find_social_links(links, username)
    youtube = find_youtube(links, username)

    # 🔥 TOTAL SCORE
    total_score = sum([s["score"] for s in socials])

    if youtube:
        total_score += youtube[0]["score"]

    confidence = calculate_confidence(total_score)

    return {
        "email": email,
        "domain": domain,
        "company": company,
        "social_profiles": socials,
        "youtube_channels": youtube,
        "confidence": confidence,
        "score": total_score
    }
