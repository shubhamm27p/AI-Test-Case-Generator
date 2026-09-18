import logging
from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from ..llm.client import LLMClient
from ..models.test_case import TestCase
from ..exceptions import GenerationError

logger = logging.getLogger(__name__)

class PyTestCode(BaseModel):
    code: str = Field(description="The complete executable Python code for PyTest.")

class PyTestGenerator:
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
        self.mode = self.llm_client.mode

    def generate_code(self, test_cases: List[TestCase], requirement: str, code_context: str = "") -> str:
        if not test_cases:
            raise GenerationError("Cannot generate code for empty test cases.")
            
        if self.mode == "mock":
            return self._mock_pytest_code()
            
        # Serialize test cases that are marked as automatable
        automatable_cases = [tc for tc in test_cases if tc.automation_possible]
        if not automatable_cases:
            return "# No automatable test cases provided."
            
        test_cases_json = "\n".join([tc.model_dump_json() for tc in automatable_cases])
        
        json_template = '''
You MUST return a JSON object with EXACTLY this structure and key:
{{
  "code": "string (The complete executable Python code for PyTest)"
}}
'''
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert SDET (Software Development Engineer in Test). "
                       "If 'Code Context' IS provided, generate the complete, valid, executable PyTest code matching the context. "
                       "If 'Code Context' IS EMPTY or UNAVAILABLE, DO NOT invent fake APIs, URLs, or implementation details. "
                       "Instead, generate clearly structured PyTest templates/mocks, and add a comment at the very top: '# TEMPLATE: Automation requires target implementation details.' "
                       f"Do not use external APIs or run shell commands. Ensure standard imports like pytest are included. Return ONLY valid Python code. Output strictly in JSON format.\n\n{json_template}"),
            ("human", "Requirement:\n{requirement}\n\nCode Context:\n{code_context}\n\nTest Cases:\n{test_cases}")
        ])
        
        try:
            structured_llm = self.llm_client.get_model().with_structured_output(PyTestCode, method="json_mode")
            chain = prompt | structured_llm
            result = chain.invoke({
                "requirement": requirement, 
                "code_context": code_context if code_context.strip() else "NONE_PROVIDED",
                "test_cases": test_cases_json
            })
            
            return result.code
        except Exception as e:
            logger.error(f"Failed to generate PyTest code: {e}")
            raise GenerationError(f"Failed to generate PyTest code: {str(e)}")

    def _mock_pytest_code(self) -> str:
        return '''import pytest

def test_mock_positive():
    assert True

def test_mock_negative():
    with pytest.raises(ValueError):
        raise ValueError("Mock Error")
'''
