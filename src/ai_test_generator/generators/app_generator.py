import logging
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from ..llm.client import LLMClient
from ..models.test_plan import TestPlan
from ..exceptions import GenerationError

logger = logging.getLogger(__name__)

class AppCode(BaseModel):
    code: str = Field(description="The complete, executable application implementation code.")

class AppCodeGenerator:
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
        self.mode = self.llm_client.mode

    def generate_app_code(self, requirement: str, test_plan: TestPlan) -> str:
        if not requirement:
            raise GenerationError("Cannot generate app code without a requirement.")
            
        if self.mode == "mock":
            return self._mock_app_code()
            
        json_template = '''
You MUST return a JSON object with EXACTLY this structure and key:
{{
  "code": "string (The complete executable Python code for the application)"
}}
'''
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Software Engineer. Your job is to implement the application code for the following user requirement so that the tests in the Test Plan will pass. "
                       "Write clean, functional code (e.g., using FastAPI, Flask, or pure Python classes depending on the requirement). "
                       f"Do not use external APIs or run shell commands. Ensure standard imports are included. Return ONLY valid Python code. Output strictly in JSON format.\n\n{json_template}"),
            ("human", "Requirement:\n{requirement}\n\nTest Plan:\n{test_plan}")
        ])
        
        try:
            structured_llm = self.llm_client.get_model().with_structured_output(AppCode, method="json_mode")
            chain = prompt | structured_llm
            result = chain.invoke({
                "requirement": requirement,
                "test_plan": test_plan.model_dump_json()
            })
            
            return result.code
        except Exception as e:
            logger.error(f"Failed to generate application code: {e}")
            raise GenerationError(f"Failed to generate application code: {str(e)}")

    def _mock_app_code(self) -> str:
        return '''def do_something():\n    return True\n'''
