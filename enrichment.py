import requests
import re

SERP_API_KEY = "322a4b39b63f54322883467960ae962f6198a3bc898de77da993a308c4c76384"


# 🔍 Search via SerpAPI
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
    except Exception as e:
        print("ERROR:", e)
        return []


# 🧠 Score links
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

    if any(x in l for x in ["video", "news"]):
        score -= 10

    if any(x in l for x in ["group", "marketplace"]):
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


# 🌐 Social selection (UPDATED FILTERS)
def find_social_links(links, company):
    company_lower = company.lower()

    best = {}
    fallback = {}

    for link in links:
        l = link.lower()

        # ❌ Skip junk
        if any(x in l for x in ["group", "search", "marketplace", "/posts/", "video"]):
            continue

        # ❌ Remove homepage / generic links
        if l.endswith(".com/") or l.endswith(".com"):
            continue

        if "instagram.com/?" in l:
            continue

        if "facebook.com/" in l and l.count("/") <= 3:
            continue

        # ❌ Must include company name (key upgrade)
        if company_lower not in l:
            continue

        # LinkedIn
        if "linkedin.com/company" in l:
            best["LinkedIn"] = link

        # Twitter/X
        elif "twitter.com" in l or "x.com" in l:
            if f"/{company_lower}" in l:
                best["Twitter/X"] = link
            elif "Twitter/X" not in fallback:
                fallback["Twitter/X"] = link

        # Facebook
        elif "facebook.com" in l:
            best["Facebook"] = link

        # Instagram
        elif "instagram.com" in l:
            best["Instagram"] = link

    # Add fallback if needed
    for k, v in fallback.items():
        if k not in best:
            best[k] = v

    return [{"platform": k, "url": v} for k, v in best.items()]


# 🎥 YouTube selection
def find_youtube(links, company):
    company_lower = company.lower()

    for link in links:
        if f"youtube.com/@{company_lower}" in link.lower():
            return [link]

    for link in links:
        if "youtube.com" in link and company_lower in link.lower():
            return [link]

    return []


# 🎥 Extract YouTube details + subscribers
def get_youtube_details(link):
    try:
        for suffix in ["/shorts", "/videos", "/playlists"]:
            if suffix in link:
                link = link.split(suffix)[0]

        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(link, headers=headers, timeout=5)

        html = res.text

        name = "YouTube Channel"
        if "<title>" in html:
            name = html.split("<title>")[1].split("</title>")[0]
            name = name.replace("- YouTube", "").strip()

        subs = "Unknown"
        match = re.search(r'"subscriberCountText".*?"simpleText":"([^"]+)"', html)
        if match:
            subs = match.group(1)

        return {
            "url": link,
            "name": name,
            "subscribers": subs
        }

    except:
        return {
            "url": link,
            "name": "Unknown",
            "subscribers": "Unknown"
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

    socials = find_social_links(ranked_links, company)
    youtube_links = find_youtube(ranked_links, company)

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
