from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.routers import chat, export, honesty_codings, questionnaire, session
from app.schemas import HealthResponse

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


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
