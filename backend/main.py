import logging

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from pydantic import (
    BaseModel,
    Field,
)
from backend.config import get_allowed_origins, load_backend_env


load_backend_env()

from backend.models.source import (
    ResearchSource,
)

from backend.orchestrator import run_deep_research
from backend.services.gemini_service import (
    GeminiErrorCategory,
    GeminiProviderError,
    generate_response,
)
from backend.rag.models import RAGContext
from backend.rag.service import RAGPipelineService, get_rag_pipeline_service
from backend.rag.uploaded_loader import (
    DocumentLoadError,
    MAX_UPLOAD_BYTES,
    UploadedDocumentLoader,
)


logger = logging.getLogger(__name__)


app = FastAPI(
    title="DeepResearch AI API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
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


class UploadDocumentResponse(BaseModel):
    status: str
    document_id: str
    filename: str
    file_type: str
    sections: int
    chunks: int


rag_pipeline_service: RAGPipelineService | None = None


def _get_rag_pipeline_service() -> RAGPipelineService:
    global rag_pipeline_service
    if rag_pipeline_service is None:
        rag_pipeline_service = get_rag_pipeline_service()
    return rag_pipeline_service


def _index_uploaded_document(
    data: bytes,
    filename: str,
    content_type: str | None,
):
    uploaded = UploadedDocumentLoader().load(data, filename, content_type)
    chunks = _get_rag_pipeline_service().add_uploaded_document(uploaded)
    return uploaded, chunks


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

    except GeminiProviderError as exc:
        if exc.category in {
            GeminiErrorCategory.QUOTA_EXHAUSTED,
            GeminiErrorCategory.MODEL_QUOTA_EXHAUSTED,
        }:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini free-tier quota has been reached. "
                    "Please try again later."
                ),
            ) from exc

        if exc.category == GeminiErrorCategory.TRANSIENT_UNAVAILABLE:
            raise HTTPException(
                status_code=503,
                detail=(
                    "The Gemini provider is temporarily unavailable. "
                    "Please try again shortly."
                ),
            ) from exc

        logger.exception(
            "Simple Gemini generation failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate AI response."
            ),
        ) from exc

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

        if (
            isinstance(exc, GeminiProviderError)
            and exc.category in {
                GeminiErrorCategory.QUOTA_EXHAUSTED,
                GeminiErrorCategory.MODEL_QUOTA_EXHAUSTED,
            }
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini free-tier quota has been reached. "
                    "Please try again later."
                ),
            ) from exc

        if (
            isinstance(exc, GeminiProviderError)
            and exc.category == GeminiErrorCategory.TRANSIENT_UNAVAILABLE
        ):
            raise HTTPException(
                status_code=503,
                detail=(
                    "The Gemini provider is temporarily unavailable. "
                    "Please try again shortly."
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


@app.post("/rag/documents", response_model=UploadDocumentResponse, status_code=201)
async def upload_rag_document(file: UploadFile):
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="uploaded file exceeds the 10 MB size limit")
    try:
        uploaded, chunks = await run_in_threadpool(
            _index_uploaded_document,
            data,
            file.filename or "",
            file.content_type,
        )
        return UploadDocumentResponse(
            status="indexed",
            document_id=uploaded.document.source_id,
            filename=uploaded.filename,
            file_type=uploaded.extension,
            sections=uploaded.section_count,
            chunks=len(chunks),
        )
    except DocumentLoadError as exc:
        message = str(exc)
        status_code = 415 if "unsupported file type" in message else 400
        raise HTTPException(status_code=status_code, detail=message) from exc
    except Exception as exc:
        logger.exception("Uploaded document indexing failed.")
        raise HTTPException(status_code=502, detail="Document indexing failed.") from exc