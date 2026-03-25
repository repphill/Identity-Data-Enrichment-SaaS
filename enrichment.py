def enrich_email(email):
    domain = email.split("@")[-1]
    company = domain.replace(".com", "")

    html = ""

    # 🔥 Company-based searches
    html += search_web(f"{company} official website")
    html += search_web(f"{company} linkedin")
    html += search_web(f"{company} twitter")
    html += search_web(f"{company} facebook")
    html += search_web(f"{company} youtube")

    links = extract_links(html)

    socials = find_social_links(links)
    youtube = find_youtube(links)

    # Remove duplicates
    socials = list({s['url']: s for s in socials}.values())
    youtube = list(set(youtube))

    if socials or youtube:
        confidence = "high"
    else:
        confidence = "low"

    return {
        "email": email,
        "domain": domain,
        "company": company,
        "social_profiles": socials[:5],
        "youtube_channels": youtube[:5],
        "confidence": confidence
    }
