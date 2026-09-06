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
from backend.rag.models import RAGContext
from backend.rag.service import RAGPipelineService


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


class RAGRetrieveRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RAGRetrieveResponse(RAGContext):
    pass


rag_pipeline_service: RAGPipelineService | None = None


def _get_rag_pipeline_service() -> RAGPipelineService:
    global rag_pipeline_service
    if rag_pipeline_service is None:
        rag_pipeline_service = RAGPipelineService()
    return rag_pipeline_service


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


@app.post(
    "/rag/retrieve",
    response_model=RAGRetrieveResponse,
)
def retrieve_rag_context(
    request: RAGRetrieveRequest,
):
    if not request.question.strip():
        raise HTTPException(status_code=422, detail="question cannot be blank")
    try:
        return _get_rag_pipeline_service().retrieve(
            request.question,
            top_k=request.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("RAG retrieval failed.")
        raise HTTPException(
            status_code=502,
            detail="RAG retrieval failed.",
        ) from exc