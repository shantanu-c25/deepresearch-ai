import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import (
    BaseModel,
    Field,
)
from backend.models.source import (
    ResearchSource,
)

from backend.orchestrator import run_deep_research
from backend.services.gemini_service import generate_response


logger = logging.getLogger(__name__)


app = FastAPI(
    title="DeepResearch AI API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    response: str


class ResearchRequest(BaseModel):
    question: str


class ResearchResponse(BaseModel):
    question: str

    research_brief: str

    critical_analysis: str

    insights: str

    final_report: str

    sources: list[
        ResearchSource
    ] = Field(
        default_factory=list
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "deep-research-api",
    }


@app.post(
    "/ai/generate",
    response_model=GenerateResponse,
)
def generate_ai_response(
    request: GenerateRequest,
):
    try:
        response = generate_response(
            request.prompt
        )

        return {
            "response": response,
        }

    except Exception:
        logger.exception(
            "Simple Gemini generation failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate AI response."
            ),
        )


@app.post(
    "/research",
    response_model=ResearchResponse,
)
def run_research(
    request: ResearchRequest,
):
    try:
        return run_deep_research(
            request.question
        )

    except Exception as exc:
        error_code = getattr(
            exc,
            "code",
            None,
        )

        if error_code == 429:
            logger.warning(
                "Deep research stopped because "
                "the Gemini quota was exhausted."
            )

            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini free-tier quota "
                    "has been reached. "
                    "Please try again later."
                ),
            ) from exc

        logger.exception(
            "Deep research failed "
            "with an unexpected error."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to complete "
                "deep research."
            ),
        ) from exc