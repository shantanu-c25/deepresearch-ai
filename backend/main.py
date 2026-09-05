from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.services.gemini_service import generate_response


app = FastAPI(
    title="DeepResearch AI API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    response: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "deep-research-api",
    }


@app.post("/ai/generate", response_model=GenerateResponse)
def generate_ai_response(request: GenerateRequest):
    try:
        response = generate_response(request.prompt)

        return {
            "response": response,
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI response.",
        )