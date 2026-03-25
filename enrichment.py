import requests

SERP_API_KEY = "322a4b39b63f54322883467960ae962f6198a3bc898de77da993a308c4c76384"


# 🔍 Search
def search_google(query):
    url = "https://serpapi.com/search"

    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "engine": "google",
        "num": 5
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()
        return data.get("organic_results", [])
    except:
        return []


# 🧠 SCORE LINKS (LESS STRICT)
def score_link(link, company):
    l = link.lower()
    company = company.lower()

    score = 0

    if company in l:
        score += 30

    if f"/{company}" in l:
        score += 20

    if "official" in l:
        score += 10

    # Penalize junk lightly (NOT too aggressive)
    if "video" in l or "news" in l:
        score -= 10

    if "group" in l:
        score -= 20

    return score


# 🔗 Rank links
def extract_ranked_links(results, company):
    scored = []

    for r in results:
        link = r.get("link")
        if not link:
            continue

        s = score_link(link, company)
        scored.append((s, link))

    scored.sort(reverse=True)

    return [link for _, link in scored]


# 🌐 SOCIAL SELECTION (RELAXED)
def find_social_links(links, company):
    company_lower = company.lower()

    best = {}
    fallback = {}

    for link in links:
        l = link.lower()

        # ❌ Skip junk
        if any(x in l for x in ["group", "search", "marketplace", "/posts/", "video"]):
            continue

        # LinkedIn
        if "linkedin.com/company" in l:
            best["LinkedIn"] = link

        # Twitter/X (PRIORITY FIX)
        elif "twitter.com" in l or "x.com" in l:
            if f"/{company_lower}" in l:
                best["Twitter/X"] = link  # exact match wins
            elif "Twitter/X" not in fallback:
                fallback["Twitter/X"] = link  # backup option

        # Facebook
        elif "facebook.com" in l:
            best["Facebook"] = link

        # Instagram
        elif "instagram.com" in l:
            best["Instagram"] = link

    # Merge best + fallback
    for k, v in fallback.items():
        if k not in best:
            best[k] = v

    return [{"platform": k, "url": v} for k, v in best.items()]

# 🎥 YOUTUBE (RELAXED)
def find_youtube(links):
    yt = []

    for link in links:
        if "youtube.com" in link:
            yt.append(link)

    return list(set(yt))[:1]


# 🎥 Extract name
def get_youtube_details(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(link, headers=headers, timeout=5)

        html = res.text
        name = "YouTube Channel"

        if "<title>" in html:
            name = html.split("<title>")[1].split("</title>")[0]
            name = name.replace("- YouTube", "").strip()

        return {
            "url": link,
            "name": name
        }

    except:
        return {
            "url": link,
            "name": "Unknown"
        }


# 🧠 MAIN FUNCTION
def enrich_email(email):
    domain = email.split("@")[-1]
    company = domain.replace(".com", "")

    results = []

    results += search_google(f"{company} linkedin")
    results += search_google(f"{company} twitter")
    results += search_google(f"{company} facebook")
    results += search_google(f"{company} instagram")
    results += search_google(f"{company} youtube")

    ranked_links = extract_ranked_links(results, company)

    socials = find_social_links(ranked_links)
    youtube_links = find_youtube(ranked_links)

    youtube = [get_youtube_details(link) for link in youtube_links]

    confidence = "high" if socials or youtube else "low"

    return {
        "email": email,
        "domain": domain,
        "company": company,
        "social_profiles": socials,
        "youtube_channels": youtube,
        "confidence": confidence
    }
