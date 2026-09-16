from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agno AI Agent"
    environment: str = "development"
    
    # LLM Settings
    llm_provider: str = "deepseek"  # google, deepseek, groq, ollama, mock
    default_model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2048

    # API Keys & URLs
    google_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    nvidia_api_key: Optional[str] = "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"
    ollama_base_url: str = "http://localhost:11434/v1"

    # Paths
    data_dir: Path = Path(__file__).parent / "data"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
