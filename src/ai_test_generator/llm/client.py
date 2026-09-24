import logging
from langchain_openai import ChatOpenAI
from ..config import load_config, resolve_model_name
from ..exceptions import LLMError

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, config=None):
        self.config = config or load_config()
        self.mode = self.config.mode
        
        if self.mode != "mock":
            base_url = self.config.openai_base_url or "https://api.openai.com/v1"
            api_key = self.config.openai_api_key or "ollama"

            if not self.config.openai_api_key and not base_url.startswith("http://localhost:11434"):
                raise LLMError("OpenAI API key is not configured. Add OPENAI_API_KEY to your .env file or Streamlit secrets.")

            model_name = resolve_model_name(self.config.openai_model)
            try:
                self.llm = ChatOpenAI(
                    api_key=api_key,
                    base_url=base_url,
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
