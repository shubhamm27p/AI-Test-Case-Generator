"""
Configuration settings for AI Test Generator
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

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

    return AppConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL", None),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        huggingface_api_key=os.getenv("HUGGINGFACE_API_KEY", ""),
        huggingface_model=os.getenv("HUGGINGFACE_MODEL", "distilbert-base-uncased"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        mode=os.getenv("AI_TEST_GEN_MODE", "live").lower(),
        execution_timeout=int(os.getenv("EXECUTION_TIMEOUT", "30")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        output_dir=os.getenv("OUTPUT_DIR", "tests/"),
        sandbox_type=os.getenv("SANDBOX_TYPE", "local").lower()
    )
