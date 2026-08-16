"""Environment / app configuration settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "renti-backend"
    # API keys live only in .env (never committed). Empty => mock/offline mode for dev.
    gemini_api_key: str = ""
    groq_api_key: str = ""
    llm_primary_provider: str = "gemini/gemini-2.0-flash"
    llm_fallback_provider: str = "groq/llama-3.3-70b-versatile"
    llm_per_provider_timeout: float = 7.0
    llm_total_deadline: float = 12.0
    # Team ID Gemastik & SQLite database path
    team_id: str = "RENTI-TEAM-01"
    db_path: str = "renti.db"
    # Crisis/referral contact (verify before public demo - see TAHAPAN PEMBELAJARAN §9).
    crisis_hotline: str = "119"


@lru_cache
def get_settings() -> Settings:
    return Settings()
