import requests

SERP_API_KEY = "322a4b39f54322883467960ae962f6198a3bc898de77da993a308c4c76384"


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


# 🧠 SCORE LINKS (KEY UPGRADE)
def score_link(link, company):
    l = link.lower()
    company = company.lower()

    score = 0

    if company in l:
        score += 50

    if f"/{company}" in l:
        score += 30

    if "official" in l:
        score += 20

    if "youtube.com/@" + company in l:
        score += 40

    # Penalize junk
    if any(x in l for x in ["video", "groups", "posts", "news"]):
        score -= 50

    if any(x in l for x in ["fan", "unofficial"]):
        score -= 100

    return score


# 🔗 Extract + rank best links
def extract_best_links(results, company):
    scored = []

    for r in results:
        link = r.get("link")
        if not link:
            continue

        s = score_link(link, company)
        scored.append((s, link))

    # Sort best first
    scored.sort(reverse=True)

    return [link for _, link in scored]


# 🌐 PICK BEST SOCIAL PER PLATFORM
def find_best_socials(links, company):
    best = {}

    for link in links:
        l = link.lower()

        if "linkedin.com/company" in l and "LinkedIn" not in best:
            best["LinkedIn"] = link

        elif ("twitter.com" in l or "x.com" in l) and "Twitter/X" not in best:
            best["Twitter/X"] = link

        elif "facebook.com" in l and "Facebook" not in best:
            if "video" not in l:
                best["Facebook"] = link

        elif "instagram.com" in l and "Instagram" not in best:
            best["Instagram"] = link

    return [{"platform": k, "url": v} for k, v in best.items()]


# 🎥 PICK BEST YOUTUBE
def find_best_youtube(links, company):
    for link in links:
        l = link.lower()

        # Prefer @handle
        if f"youtube.com/@{company}" in l:
            return [link]

    # fallback to any youtube
    for link in links:
        if "youtube.com" in link:
            return [link]

    return []


# 🎥 Extract channel name
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

    results += search_google(f"{company} linkedin company")
    results += search_google(f"{company} twitter")
    results += search_google(f"{company} facebook")
    results += search_google(f"{company} instagram")
    results += search_google(f"{company} youtube")

    ranked_links = extract_best_links(results, company)

    socials = find_best_socials(ranked_links, company)
    youtube_links = find_best_youtube(ranked_links, company)

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
