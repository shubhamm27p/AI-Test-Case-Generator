import logging
from langchain_core.prompts import ChatPromptTemplate
from ..llm.client import LLMClient
from ..models.test_plan import TestPlan
from ..exceptions import GenerationError

logger = logging.getLogger(__name__)

class RequirementAnalyzer:
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
        self.mode = self.llm_client.mode

    def analyze_requirement(self, requirement: str, code_context: str = "", include_api: bool = False, include_performance: bool = False) -> TestPlan:
        if not requirement or not requirement.strip():
            raise GenerationError("Requirement input cannot be empty.")
            
        if self.mode == "mock":
            return self._mock_test_plan(requirement)
            
        system_msg = "You are an expert QA Architect. Your job is to analyze the following user requirement and any provided code context to generate a comprehensive Test Plan. Output strictly in JSON format."
        if include_api:
            system_msg += " Make sure to explicitly define an API testing strategy."
        if include_performance:
            system_msg += " Make sure to explicitly define performance testing criteria and thresholds."
        json_template = '''
You MUST return a JSON object with EXACTLY these keys (do not add or remove keys):
{{
  "feature_name": "string",
  "objective": "string",
  "scope": "string",
  "assumptions": ["string"],
  "testing_approach": "string",
  "test_types": ["string"],
  "risks": ["string"],
  "dependencies": ["string"],
  "environment_requirements": "string",
  "out_of_scope_items": ["string"],
  "api_testing_strategy": "string or null",
  "performance_criteria": "string or null"
}}
'''
        system_msg += json_template
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human", "Requirement:\n{requirement}\n\nCode Context:\n{code_context}")
        ])
        
        try:
            structured_llm = self.llm_client.get_model().with_structured_output(TestPlan, method="json_mode")
            chain = prompt | structured_llm
            result = chain.invoke({"requirement": requirement, "code_context": code_context})
            return result
        except Exception as e:
            logger.error(f"Failed to generate Test Plan: {e}")
            raise GenerationError(f"Failed to generate Test Plan: {str(e)}")

    def _mock_test_plan(self, requirement: str) -> TestPlan:
        return TestPlan(
            feature_name="Mock Feature Registration",
            objective="To verify the mock requirement.",
            scope="Basic mock scope. Testing core functionality.",
            assumptions=["System is running", "Database is accessible"],
            testing_approach="Automated PyTest testing",
            test_types=["Positive", "Negative", "Boundary"],
            risks=["Network latency in mock"],
            dependencies=["Mock Auth Service"],
            environment_requirements="Local",
            out_of_scope_items=["Load testing", "Security testing"]
        )
