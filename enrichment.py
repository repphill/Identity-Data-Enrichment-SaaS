import requests

# 🔐 YOUR SERP API KEY (replace if you rotate it later)
SERP_API_KEY = "322a4b39b63f54322883467960ae962f6198a3bc898de77da993a308c4c76384"


# 🔍 Google search via SerpAPI
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
    links = []

    for r in results:
        link = r.get("link")
        if link:
            links.append(link)

    return links


# 🌐 CLEAN SOCIAL FILTER (STEP 1 UPGRADE)
def find_social_links(links):
    socials = []

    for link in links:
        lower = link.lower()

        # ❌ Remove junk
        if "group" in lower or "search" in lower:
            continue

        # ✅ Keep high-quality pages
        if "linkedin.com/company" in lower:
            socials.append({"platform": "LinkedIn", "url": link})

        elif "twitter.com" in lower or "x.com" in lower:
            socials.append({"platform": "Twitter/X", "url": link})

        elif "facebook.com" in lower and ("pages" in lower or "official" in lower):
            socials.append({"platform": "Facebook", "url": link})

        elif "instagram.com" in lower:
            socials.append({"platform": "Instagram", "url": link})

    return socials


# 🎥 ADVANCED YOUTUBE EXTRACTION (STEP 2 UPGRADE)
def find_youtube(links):
    yt = []

    for link in links:
        if "youtube.com" in link and ("channel" in link or "@" in link):
            yt.append(link)

    return yt


# 🎥 GET YOUTUBE CHANNEL DETAILS
def get_youtube_details(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(link, headers=headers, timeout=5)

        html = res.text

        # Basic extraction (simple but effective)
        title = "Unknown Channel"

        if "<title>" in html:
            title = html.split("<title>")[1].split("</title>")[0]

        return {
            "url": link,
            "name": title.replace("- YouTube", "").strip()
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

    # 🔥 Targeted queries
    results += search_google(f"{company} linkedin")
    results += search_google(f"{company} twitter")
    results += search_google(f"{company} facebook official")
    results += search_google(f"{company} instagram")
    results += search_google(f"{company} youtube")

    links = extract_links(results)

    socials = find_social_links(links)
    youtube_links = find_youtube(links)

    # Remove duplicates
    socials = list({s['url']: s for s in socials}.values())
    youtube_links = list(set(youtube_links))

    # 🎥 Get YouTube details
    youtube = [get_youtube_details(link) for link in youtube_links[:3]]

    confidence = "high" if socials or youtube else "low"

    return {
        "email": email,
        "domain": domain,
        "company": company,
        "social_profiles": socials[:5],
        "youtube_channels": youtube,
        "confidence": confidence
    }
