from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import csv
import uuid

from enrichment import enrich_email

app = FastAPI()


# 🔹 Single email endpoint (keep this)
@app.post("/enrich")
async def enrich(data: dict):
    return enrich_email(data["email"])


# 🔥 BULK CSV ENRICHMENT
@app.post("/bulk-enrich")
async def bulk_enrich(file: UploadFile = File(...)):

    # Save uploaded file
    input_path = f"/tmp/{uuid.uuid4()}.csv"
    output_path = f"/tmp/output_{uuid.uuid4()}.csv"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    results = []

    # Read CSV
    with open(input_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            email = row.get("email")

            if not email:
                continue

            data = enrich_email(email)

            # Extract fields
            socials = {s["platform"]: s["url"] for s in data["social_profiles"]}

            youtube = data["youtube_channels"][0] if data["youtube_channels"] else {}

            results.append({
                "email": email,
                "company": data["company"],
                "linkedin": socials.get("LinkedIn", ""),
                "twitter": socials.get("Twitter/X", ""),
                "instagram": socials.get("Instagram", ""),
                "facebook": socials.get("Facebook", ""),
                "youtube": youtube.get("url", ""),
                "subscribers": youtube.get("subscribers", "")
            })

    # Write output CSV
    with open(output_path, "w", newline="") as csvfile:
        fieldnames = [
            "email", "company", "linkedin", "twitter",
            "instagram", "facebook", "youtube", "subscribers"
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return FileResponse(output_path, filename="enriched_results.csv")
