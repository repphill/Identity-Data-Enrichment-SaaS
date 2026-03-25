import requests

# 🔐 Replace this if you rotate your key later
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


# 🔗 Extract links
def extract_links(results):
    return [r.get("link") for r in results if r.get("link")]


# 🌐 CLEAN SOCIAL FILTER (FINAL VERSION)
def find_social_links(links, company):
    socials = {}
    company_lower = company.lower()

    for link in links:
        l = link.lower()

        # ❌ Skip junk
        if "group" in l or "search" in l or "/posts/" in l:
            continue

        # ❌ Skip unofficial pages
        if "unofficial" in l or "fan" in l:
            continue

        # ✅ LinkedIn (best match)
        if "linkedin.com/company" in l:
            if company_lower in l:
                socials["LinkedIn"] = link

        # ✅ Twitter/X
        elif "twitter.com" in l or "x.com" in l:
            if company_lower in l:
                socials["Twitter/X"] = link

        # ✅ Facebook
        elif "facebook.com" in l:
            if company_lower in l and "groups" not in l:
                socials["Facebook"] = link

        # ✅ Instagram
        elif "instagram.com" in l:
            if company_lower in l:
                socials["Instagram"] = link

    return [{"platform": k, "url": v} for k, v in socials.items()]


# 🎥 YouTube detection (clean)
def find_youtube(links, company):
    yt = []
    company_lower = company.lower()

    for link in links:
        l = link.lower()

        if "youtube.com" in l:
            if company_lower in l:
                yt.append(link)

    return list(set(yt))[:2]


# 🎥 Extract YouTube channel name
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

    # 🔥 Strong targeted queries
    results += search_google(f"{company} linkedin company")
    results += search_google(f"{company} official twitter")
    results += search_google(f"{company} official facebook")
    results += search_google(f"{company} instagram")
    results += search_google(f"{company} youtube official")

    links = extract_links(results)

    socials = find_social_links(links, company)
    youtube_links = find_youtube(links, company)

    # 🎥 Get YouTube channel details
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
