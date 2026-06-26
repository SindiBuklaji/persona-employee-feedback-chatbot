from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    database_url: str = "sqlite:///./thesis_chatbot.db"
    min_turns: int = 3
    max_turns: int = 5
    temperature: float = 1.0
    top_k_retrieval: int = 3
    allowed_origins: str = "http://localhost:8501"
    debug: bool = False
    admin_token: str = ""

    # Retrieval configuration
    retrieval_enabled: bool = True
    retrieval_use_embeddings: bool = True
    retrieval_logging_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
