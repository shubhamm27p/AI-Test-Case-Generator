"""
Configuration settings for AI Test Generator
"""
import os
from dataclasses import dataclass
from typing import Optional, Any
from dotenv import load_dotenv

# Mapping of deprecated or unsupported model names to active compatible replacements.
MODEL_ALIASES = {
    "gemini-1.5-flash": "gemini-2.5-flash",
    "gemini-1.5-flash-latest": "gemini-2.5-flash",
    "gemini-1.5-pro": "gemini-2.5-pro",
    "gemini-1.5-pro-latest": "gemini-2.5-pro",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-3.1-pro-preview": "gemini-2.5-pro",
    "gemini-3.6-flash": "gemini-2.5-flash",
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


def _get_setting(key: str, default: Any = None) -> Any:
    val = os.getenv(key)
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
    if config_path and os.path.exists(config_path):
        load_dotenv(config_path, override=False)
    else:
        load_dotenv(override=False)

    raw_model = _get_setting("OPENAI_MODEL", "gpt-4o-mini")
    resolved_model = resolve_model_name(raw_model)

    return AppConfig(
        openai_api_key=_get_setting("OPENAI_API_KEY", ""),
        openai_base_url=_get_setting("OPENAI_BASE_URL", None),
        openai_model=resolved_model,
        huggingface_api_key=_get_setting("HUGGINGFACE_API_KEY", ""),
        huggingface_model=_get_setting("HUGGINGFACE_MODEL", "distilbert-base-uncased"),
        log_level=str(_get_setting("LOG_LEVEL", "INFO")).upper(),
        mode=str(_get_setting("AI_TEST_GEN_MODE", "live")).lower(),
        execution_timeout=int(_get_setting("EXECUTION_TIMEOUT", "30")),
        max_retries=int(_get_setting("MAX_RETRIES", "3")),
        output_dir=_get_setting("OUTPUT_DIR", "tests/"),
        sandbox_type=str(_get_setting("SANDBOX_TYPE", "local")).lower()
    )
