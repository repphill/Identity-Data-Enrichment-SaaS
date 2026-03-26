from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import csv
import io

from enrichment import enrich_email

app = FastAPI()

# =========================
# 🌐 CORS (IMPORTANT)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"status": "running"}


# =========================
# 🔍 SINGLE EMAIL
# =========================
@app.post("/enrich")
async def enrich(email: str):
    try:
        data = enrich_email(email)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 📂 BULK CSV (FULL FIX)
# =========================
@app.post("/bulk-enrich")
async def bulk_enrich(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # 🔥 FIX: handle encoding safely
        decoded = contents.decode("utf-8", errors="ignore")

        reader = csv.DictReader(io.StringIO(decoded))

        results = []

        for row in reader:
            email = (
                row.get("email") or
                row.get("Email") or
                row.get("EMAIL")
            )

            if not email:
                continue

            data = enrich_email(email)

            socials = {s["platform"]: s["url"] for s in data["social_profiles"]}
            youtube = data["youtube_channels"][0] if data["youtube_channels"] else {}

            results.append({
                "email": data["email"],
                "company": data["company"],
                "linkedin": socials.get("LinkedIn", ""),
                "twitter": socials.get("Twitter/X", ""),
                "instagram": socials.get("Instagram", ""),
                "facebook": socials.get("Facebook", ""),
                "youtube": youtube.get("url", ""),
                "subscribers": youtube.get("subscribers", ""),
                "confidence": data["confidence"],
                "score": data["score"]
            })

        # 🔥 BUILD CSV OUTPUT
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            "email", "company", "linkedin", "twitter",
            "instagram", "facebook", "youtube",
            "subscribers", "confidence", "score"
        ])

        writer.writeheader()
        writer.writerows(results)

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=enriched.csv"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
