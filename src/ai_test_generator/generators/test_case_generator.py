import logging
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from ..llm.client import LLMClient
from ..models.test_plan import TestPlan
from ..models.test_case import TestSuite, TestCase
from ..exceptions import GenerationError

logger = logging.getLogger(__name__)

class TestCaseGenerator:
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
        self.mode = self.llm_client.mode

    def generate_test_cases(self, requirement: str, test_plan: TestPlan, code_context: str = "", include_api: bool = False, include_performance: bool = False) -> List[TestCase]:
        if not requirement or not requirement.strip():
            raise GenerationError("Requirement input cannot be empty.")
            
        if self.mode == "mock":
            return self._mock_test_cases()
            
        system_msg = "You are an expert QA Automation Engineer. Based on the Requirement, Code Context, and Test Plan, generate a comprehensive suite of Test Cases covering Positive, Negative, Boundary, Edge Cases, Error Handling, and Validation scenarios where applicable. Avoid duplicate scenarios. Provide complete and realistic test data and steps. IMPORTANT: For each test case, generate the actual PyTest code in the 'code_snippet' field (do not leave it null, write the real code implementation or a robust stub). Output strictly in JSON format."
        if include_api:
            system_msg += " Specifically ensure you generate test cases targeting API endpoints and populate the 'api_endpoint' field."
        if include_performance:
            system_msg += " Specifically ensure you generate performance/load test cases and populate the 'performance_threshold' field."
        json_template = '''
You MUST return a JSON object with EXACTLY this structure and keys:
{{
  "test_cases": [
    {{
      "test_case_id": "string",
      "title": "string",
      "description": "string",
      "preconditions": ["string"],
      "test_data": {{"key": "value"}},
      "steps": ["string"],
      "expected_result": "string",
      "test_type": "string",
      "priority": "string",
      "severity": "string",
      "automation_possible": true,
      "tags": ["string"],
      "api_endpoint": "string or null",
      "performance_threshold": "string or null",
      "code_snippet": "string or null"
    }}
  ]
}}
'''
        system_msg += json_template
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human", "Requirement:\n{requirement}\n\nCode Context:\n{code_context}\n\nTest Plan:\n{test_plan}")
        ])
        
        try:
            structured_llm = self.llm_client.get_model().with_structured_output(TestSuite, method="json_mode")
            chain = prompt | structured_llm
            result = chain.invoke({
                "requirement": requirement, 
                "code_context": code_context,
                "test_plan": test_plan.model_dump_json()
            })
            
            if not result or not result.test_cases:
                raise GenerationError("LLM returned empty test cases.")
                
            return result.test_cases
        except Exception as e:
            logger.error(f"Failed to generate Test Cases: {e}")
            raise GenerationError(f"Failed to generate Test Cases: {str(e)}")

    def _mock_test_cases(self) -> List[TestCase]:
        return [
            TestCase(
                test_case_id="TC-001",
                title="Mock Positive Test",
                description="Verifies the positive path",
                preconditions=["System running"],
                test_data={"input": "valid"},
                steps=["Step 1", "Step 2"],
                expected_result="Success",
                test_type="Positive",
                priority="High",
                severity="Critical",
                automation_possible=True,
                tags=["mock", "positive"]
            ),
            TestCase(
                test_case_id="TC-002",
                title="Mock Negative Test",
                description="Verifies the negative path",
                preconditions=["System running"],
                test_data={"input": "invalid"},
                steps=["Step 1", "Step 2"],
                expected_result="Failure with error message",
                test_type="Negative",
                priority="Medium",
                severity="Major",
                automation_possible=True,
                tags=["mock", "negative"]
            )
        ]
