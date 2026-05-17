"""Application settings for PneumoScan AI."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────
    app_name: str = Field(default="PneumoScan AI")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)

    # ── Server ───────────────────────────────────────────────
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # ── CORS ─────────────────────────────────────────────────
    allowed_origins: str = Field(default="http://localhost:3000,http://127.0.0.1:3000")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip().rstrip("/") for origin in self.allowed_origins.split(",") if origin.strip()]

    # ── ML Model ─────────────────────────────────────────────
    model_path: str = Field(default="ml_models/densenet121_pneumonia_model.h5")
    model_input_size: int = Field(default=224)
    model_version: str = Field(default="DenseNet121-v2")
    gradcam_layer_name: str = Field(default="conv5_block16_concat")
    confidence_threshold: float = Field(default=0.5)

    # ── Supabase ─────────────────────────────────────────────
    supabase_url: str = Field(default="")
    supabase_key: str = Field(default="")
    supabase_service_key: str = Field(default="")
    supabase_bucket: str = Field(default="xray-images")

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    @property
    def resolved_model_path(self) -> Path:
        path = Path(self.model_path).expanduser()
        return path if path.is_absolute() else BACKEND_DIR / path

    @property
    def supabase_enabled(self) -> bool:
        supabase_url = self.supabase_url.strip().strip('"').strip("'")
        supabase_service_key = self.supabase_service_key.strip().strip('"').strip("'")
        placeholder_values = {
            "",
            "YOUR_URL",
            "YOUR_ANON_KEY",
            "YOUR_SERVICE_ROLE_KEY",
            "your-url",
            "your-supabase-anon-key",
            "your-supabase-service-role-key",
            "YOUR_SUPABASE_ANON_KEY",
            "YOUR_SUPABASE_SERVICE_ROLE_KEY",
        }
        return (
            supabase_url not in placeholder_values
            and supabase_service_key not in placeholder_values
            and "your-project-id" not in supabase_url
            and supabase_url.startswith("https://")
        )


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached singleton Settings instance.
    lru_cache() means we only read/validate .env once, not per-request.
    """
    return Settings()


# Convenience alias used throughout the codebase
settings = get_settings()
