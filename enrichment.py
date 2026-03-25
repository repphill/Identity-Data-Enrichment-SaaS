import requests

# 🔐 YOUR SERP API KEY
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
    except:
        return []


# 🔗 Extract links
def extract_links(results):
    links = []

    for r in results:
        link = r.get("link")
        if link:
            links.append(link)

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


# 🧠 MAIN FUNCTION
def enrich_email(email):
    domain = email.split("@")[-1]
    company = domain.replace(".com", "")

    results = []

    # 🔥 Strong targeted queries
    results += search_google(f"{company} official website")
    results += search_google(f"{company} linkedin")
    results += search_google(f"{company} twitter")
    results += search_google(f"{company} facebook")
    results += search_google(f"{company} instagram")
    results += search_google(f"{company} youtube")

    links = extract_links(results)

    socials = find_social_links(links)
    youtube = find_youtube(links)

    # Remove duplicates
    socials = list({s['url']: s for s in socials}.values())
    youtube = list(set(youtube))

    # Confidence logic
    confidence = "high" if socials or youtube else "low"

    return {
        "email": email,
        "domain": domain,
        "company": company,
        "social_profiles": socials[:5],
        "youtube_channels": youtube[:5],
        "confidence": confidence
    }
