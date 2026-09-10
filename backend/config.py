"""
Backend Configuration for BEM 100 v2.0.
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "BEM 100 v2.0 Market Engine"
    app_version: str = "2.0.0"
    environment: str = os.getenv("ENV", "production")
    supabase_url: str = os.getenv("SUPABASE_URL", "").strip()
    supabase_key: str = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")).strip()
    cors_origins: list[str] = ["*"]
    cache_dir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


settings = Settings()
