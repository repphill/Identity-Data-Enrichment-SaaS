from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import csv
import io
import stripe

# 🔥 IMPORT YOUR ENRICHMENT LOGIC
from enrichment import enrich_email

# 🔐 FIREBASE
import firebase_admin
from firebase_admin import credentials, auth

# =========================
# 🔐 FIREBASE SETUP
# =========================
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

# =========================
# 💳 STRIPE SETUP
# =========================
stripe.api_key = "sk_test_YOUR_SECRET_KEY"  # 🔥 sk_test_51TF0IQQrPUguvXjd6OPZG8Oh2nk9Ovdgg9Yp6KJXHLsS5ziqi4MWV3xRJB0BchiuHpwVytx4cU3v57GudPHOvrPY00S0CmNOjq

PRICE_ID = "price_1TF0M8Jrm29WCuxScCITllS1"

# =========================
# 🚀 FASTAPI INIT
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔐 VERIFY USER TOKEN
# =========================
def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        token = auth_header.split(" ")[1]
        decoded = auth.verify_id_token(token)
        return decoded
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


# =========================
# 💳 TEMP PAYWALL (TEST ONLY)
# =========================
def is_paid_user(user):
    # 🔥 TEMP: only allow this email
    return user.get("email") == "test@test.com"


# =========================
# 🏠 ROOT
# =========================
@app.get("/")
def root():
    return {"message": "API is running"}


# =========================
# 💳 STRIPE CHECKOUT
# =========================
@app.get("/create-checkout")
def create_checkout():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": PRICE_ID,
            "quantity": 1,
        }],
        mode="subscription",
        success_url="https://your-vercel-app.vercel.app",
        cancel_url="https://your-vercel-app.vercel.app",
    )

    return {"url": session.url}


# =========================
# 🔍 SINGLE ENRICH
# =========================
@app.post("/enrich")
async def enrich(request: Request, email: str):
    user = verify_token(request)

    if not is_paid_user(user):
        raise HTTPException(status_code=403, detail="Upgrade required")

    return enrich_email(email)


# =========================
# 📂 BULK ENRICH
# =========================
@app.post("/bulk-enrich")
async def bulk_enrich(request: Request, file: UploadFile = File(...)):
    user = verify_token(request)

    if not is_paid_user(user):
        raise HTTPException(status_code=403, detail="Upgrade required")

    content = await file.read()
    decoded = content.decode("utf-8").splitlines()
    reader = csv.DictReader(decoded)

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV HEADER
    writer.writerow([
        "email",
        "company",
        "linkedin",
        "twitter",
        "instagram",
        "facebook",
        "youtube",
        "subscribers"
    ])

    for row in reader:
        email = row.get("email")

        if not email:
            continue

        data = enrich_email(email)

        socials = {s["platform"]: s["url"] for s in data["social_profiles"]}

        youtube = data["youtube_channels"]
        yt_url = youtube[0]["url"] if youtube else ""
        yt_subs = youtube[0]["subscribers"] if youtube else ""

        writer.writerow([
            email,
            data["company"],
            socials.get("LinkedIn", ""),
            socials.get("Twitter/X", ""),
            socials.get("Instagram", ""),
            socials.get("Facebook", ""),
            yt_url,
            yt_subs
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=enriched_results.csv"
        },
    )
