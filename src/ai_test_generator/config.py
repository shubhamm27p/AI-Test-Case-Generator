"""
Configuration settings for AI Test Generator
"""
import os
from dataclasses import dataclass
from typing import Optional, Any
from dotenv import dotenv_values

# Map stale deployment values to the current OpenAI model.
MODEL_ALIASES = {
    "gemini-1.5-flash": "gpt-4o-mini",
    "gemini-1.5-flash-latest": "gpt-4o-mini",
    "gemini-1.5-pro": "gpt-4o-mini",
    "gemini-1.5-pro-latest": "gpt-4o-mini",
    "gemini-2.5-flash": "gpt-4o-mini",
    "gemini-2.5-pro": "gpt-4o-mini",
    "gemini-3.1-pro-preview": "gpt-4o-mini",
    "gemini-3.6-flash": "gpt-4o-mini",
}

def resolve_model_name(model_name: str) -> str:
    """Return the provider-compatible name for a configured model."""
    normalized_name = model_name.strip()
    return MODEL_ALIASES.get(normalized_name, normalized_name)

@dataclass
class AppConfig:
    """Application configuration container."""
    openai_api_key: str
    openai_base_url: Optional[str]
    openai_model: str
    huggingface_api_key: str
    huggingface_model: str
    log_level: str
    mode: str
    execution_timeout: int
    max_retries: int
    output_dir: str
    test_framework: str = "pytest"
    sandbox_type: str = "local"

    def set_mode(self, mode: str) -> None:
        """Change the operation mode of the application."""
        valid_modes = ["live", "mock", "test"]
        mode = mode.lower()
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {valid_modes}")
        self.mode = mode


def _get_setting(key: str, default: Any = None, dotenv_map: Optional[dict] = None) -> Any:
    val = os.getenv(key)
    if val is not None and val != "":
        return val
    if dotenv_map is not None:
        val = dotenv_map.get(key)
        if val is not None and val != "":
            return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return default

def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load configuration from environment and .env file.
    
    Args:
        config_path: Optional path to a specific .env file.
        
    Returns:
        AppConfig instance with populated values.
    """
    env_path = config_path or ".env"
    file_values = dotenv_values(env_path) if os.path.exists(env_path) else {}

    openai_api_key = _get_setting("OPENAI_API_KEY", "", file_values)
    openai_base_url = _get_setting("OPENAI_BASE_URL", None, file_values)
    if not openai_base_url:
        openai_base_url = "http://localhost:11434/v1" if not openai_api_key else "https://api.openai.com/v1"
    if not openai_api_key and openai_base_url.startswith("http://localhost:11434"):
        openai_api_key = "ollama"

    raw_model = _get_setting("OPENAI_MODEL", "llama3.1", file_values)
    resolved_model = resolve_model_name(raw_model)

    return AppConfig(
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        openai_model=resolved_model,
        huggingface_api_key=_get_setting("HUGGINGFACE_API_KEY", "", file_values),
        huggingface_model=_get_setting("HUGGINGFACE_MODEL", "distilbert-base-uncased", file_values),
        log_level=str(_get_setting("LOG_LEVEL", "INFO", file_values)).upper(),
        mode=str(_get_setting("AI_TEST_GEN_MODE", "live", file_values)).lower(),
        execution_timeout=int(_get_setting("EXECUTION_TIMEOUT", "30", file_values)),
        max_retries=int(_get_setting("MAX_RETRIES", "3", file_values)),
        output_dir=_get_setting("OUTPUT_DIR", "tests/", file_values),
        sandbox_type=str(_get_setting("SANDBOX_TYPE", "local", file_values)).lower()
    )
