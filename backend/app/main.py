import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.routers import chat, debug, export, honesty_codings, questionnaire, session
from app.schemas import HealthResponse

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Persona Thesis Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router)
app.include_router(chat.router)
app.include_router(questionnaire.router)
app.include_router(export.router)
app.include_router(honesty_codings.router)

# Debug endpoints - only available when DEBUG=true
if settings.debug:
    app.include_router(debug.router)
    logger.info("Debug endpoints enabled at /debug/...")
else:
    logger.info("Debug endpoints disabled (set DEBUG=true to enable)")

logger.info(f"Retrieval enabled: {settings.retrieval_enabled}")
logger.info(f"Retrieval use embeddings: {settings.retrieval_use_embeddings}")
logger.info(f"Retrieval logging enabled: {settings.retrieval_logging_enabled}")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
