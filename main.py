from fastapi import FastAPI
from pydantic import BaseModel
from enrichment import enrich_email
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    email: str

@app.post("/enrich")
async def enrich(data: EmailRequest):
    return enrich_email(data.email)