import subprocess
import json
import os
from typing import Optional
from ..models.test_result import ExecutionResult, SingleTestResult
from ..config import load_config
from ..exceptions import TestExecutionError

class PyTestRunner:
    def __init__(self, config=None):
        self.config = config or load_config()
        self.timeout = self.config.execution_timeout
        
    def run_tests(self, test_file_path: str) -> ExecutionResult:
        if self.config.mode == "mock":
            return self._mock_execution_result()
            
        report_path = os.path.join(os.path.dirname(test_file_path), "report.json")
        
        # If we are using docker sandbox, the sandbox itself executes the tests during build/run
        # and mounts the report back to the test_file_path directory.
        if self.config.sandbox_type != "docker":
            cmd = [
                "pytest", 
                test_file_path, 
                "--json-report", 
                f"--json-report-file={report_path}",
                "--cov=.",
                f"--cov-report=json:{os.path.join(os.path.dirname(test_file_path), 'coverage.json')}"
            ]
            
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=self.timeout
                )
            except subprocess.TimeoutExpired:
                raise TestExecutionError(f"Test execution timed out after {self.timeout} seconds.")
            except Exception as e:
                raise TestExecutionError(f"Test execution failed: {e}")
                
        if not os.path.exists(report_path):
            raise TestExecutionError(f"Pytest report not generated. Check if pytest-json-report is installed or if Docker execution failed.")
            
        return self._parse_json_report(report_path)
        
    def _parse_json_report(self, report_path: str) -> ExecutionResult:
        with open(report_path, "r") as f:
            data = json.load(f)
            
        summary = data.get("summary", {})
        tests = data.get("tests", [])
        
        parsed_tests = []
        for t in tests:
            status = t.get("outcome", "unknown")
            err_msg = None
            if status == "failed":
                call = t.get("call", {})
                crash = call.get("crash", {})
                err_msg = crash.get("message", "Unknown error")
                
            parsed_tests.append(SingleTestResult(
                test_id=t.get("nodeid", ""),
                title=t.get("nodeid", "").split("::")[-1],
                status=status,
                duration=t.get("call", {}).get("duration", 0.0),
                error_message=err_msg
            ))
            
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        pass_percentage = (passed / total) * 100 if total > 0 else 0.0
        
        coverage_pct = None
        cov_path = os.path.join(os.path.dirname(report_path), 'coverage.json')
        if os.path.exists(cov_path):
            try:
                with open(cov_path, "r") as cf:
                    cov_data = json.load(cf)
                coverage_pct = cov_data.get("totals", {}).get("percent_covered")
            except Exception:
                pass
            
        return ExecutionResult(
            total_tests=total,
            passed=passed,
            failed=summary.get("failed", 0),
            skipped=summary.get("skipped", 0),
            errors=summary.get("error", 0),
            duration=data.get("duration", 0.0),
            pass_percentage=pass_percentage,
            coverage_percentage=coverage_pct,
            tests=parsed_tests
        )
        
    def _mock_execution_result(self) -> ExecutionResult:
        return ExecutionResult(
            total_tests=2,
            passed=1,
            failed=1,
            skipped=0,
            errors=0,
            pass_percentage=50.0,
            duration=0.5,
            tests=[
                SingleTestResult(test_id="mock_test_1", title="test_mock_positive", status="passed", duration=0.2),
                SingleTestResult(test_id="mock_test_2", title="test_mock_negative", status="failed", duration=0.3, error_message="Mock Error")
            ]
        )
