"""Configuration management for Repo2API."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # App Settings
    app_name: str = "Repo2API"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API Settings
    api_title: str = "Repo2API - REST API Generator"
    api_description: str = "Automatically convert any codebase into a REST API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api"
    
    # Server Settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    reload: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # Repository Settings
    repo_cache_dir: Path = Path(os.getenv("REPO_CACHE_DIR", "./.repo_cache"))
    max_repo_size_mb: int = int(os.getenv("MAX_REPO_SIZE_MB", "500"))
    
    # Parser Settings
    supported_languages: list = ["python"]
    ignore_patterns: list = [
        "node_modules",
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        ".env",
        "*.pyc",
        ".DS_Store",
    ]
    
    # Function Detection Settings
    ignore_private_functions: bool = True
    ignore_magic_methods: bool = True
    min_docstring_length: int = 10
    
    # Authentication (Optional)
    enable_auth: bool = os.getenv("ENABLE_AUTH", "False").lower() == "true"
    api_key_header: str = "X-API-Key"
    
    # Rate Limiting (Optional)
    enable_rate_limit: bool = os.getenv("ENABLE_RATE_LIMIT", "False").lower() == "true"
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_period_seconds: int = int(os.getenv("RATE_LIMIT_PERIOD_SECONDS", "60"))
    
    # Caching (Optional)
    enable_caching: bool = os.getenv("ENABLE_CACHING", "False").lower() == "true"
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS Settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    # OpenAPI Settings
    openapi_enabled: bool = True
    swagger_ui_enabled: bool = True
    redoc_enabled: bool = True
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the current settings instance."""
    return settings
