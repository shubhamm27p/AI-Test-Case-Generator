import logging
from langchain_openai import ChatOpenAI
from ..config import load_config
from ..exceptions import LLMError

logger = logging.getLogger(__name__)

MODEL_ALIASES = {
    "gemini-1.5-flash": "gemini-2.5-flash",
    "gemini-1.5-flash-latest": "gemini-2.5-flash",
    "gemini-1.5-pro": "gemini-2.5-pro",
    "gemini-1.5-pro-latest": "gemini-2.5-pro",
    "gemini-3.1-pro-preview": "gemini-2.5-pro",
    "gemini-3.6-flash": "gemini-2.5-flash",
}

class LLMClient:
    def __init__(self, config=None):
        self.config = config or load_config()
        self.mode = self.config.mode
        
        if self.mode != "mock":
            if not self.config.openai_api_key:
                raise LLMError("OpenAI API key is not configured. Add OPENAI_API_KEY to your .env file or Streamlit secrets.")
                
            model_name = MODEL_ALIASES.get(self.config.openai_model.strip(), self.config.openai_model.strip())
            try:
                self.llm = ChatOpenAI(
                    api_key=self.config.openai_api_key,
                    base_url=self.config.openai_base_url if self.config.openai_base_url else None,
                    model_name=model_name,
                    temperature=0.2,
                    max_retries=self.config.max_retries,
                    request_timeout=self.config.execution_timeout
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                raise LLMError(f"Failed to initialize OpenAI client: {str(e)}")
        else:
            self.llm = None

    def get_model(self):
        if self.mode == "mock":
            raise LLMError("Cannot get model in mock mode. Check mode first.")
        return self.llm
