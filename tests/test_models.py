from ai_test_generator.models.test_plan import TestPlan
from ai_test_generator.models.test_case import TestCase

def test_test_plan_creation():
    tp = TestPlan(
        feature_name="Login",
        objective="Verify login",
        scope="Frontend",
        testing_approach="Manual",
        environment_requirements="Browser"
    )
    assert tp.feature_name == "Login"
    assert tp.objective == "Verify login"

def test_test_case_creation():
    tc = TestCase(
        test_case_id="TC-01",
        title="Valid Login",
        description="Verify valid credentials",
        expected_result="User is logged in",
        test_type="Positive",
        priority="High",
        severity="Critical",
        automation_possible=True
    )
    assert tc.test_case_id == "TC-01"
