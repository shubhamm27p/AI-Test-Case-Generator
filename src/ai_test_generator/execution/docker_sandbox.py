import os
import tempfile
import subprocess
import shutil
from .sandbox import Sandbox
from ..exceptions import TestExecutionError

class DockerSandbox(Sandbox):
    def __init__(self):
        super().__init__()
        
    def write_test_file(self, code: str) -> str:
        self.validate_code(code)
        file_path = self._sandbox_path("test_generated.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        return file_path
        
    def write_app_file(self, code: str, filename: str = "app.py") -> str:
        """Writes application code to the sandbox to provide context for tests."""
        self.validate_code(code)
        file_path = self._sandbox_path(filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        return file_path
        
    def _create_dockerfile(self):
        dockerfile_content = """FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install pytest pytest-json-report pytest-cov requests fastapi uvicorn
CMD ["pytest", "test_generated.py", "--json-report", "--json-report-file=report.json", "--cov=.", "--cov-report=json:coverage.json"]
"""
        with open(os.path.join(self.temp_dir.name, "Dockerfile"), "w") as f:
            f.write(dockerfile_content)

    def execute_tests(self) -> str:
        """Builds and runs the docker container, then returns the path to the temp directory where reports are mapped."""
        # Ensure docker is installed
        if shutil.which("docker") is None:
            raise TestExecutionError("Docker is not installed or not in PATH. Cannot use DockerSandbox.")
            
        self._create_dockerfile()
        
        image_name = f"ai_test_gen_sandbox_{os.path.basename(self.temp_dir.name).lower()}"
        
        # Build image
        build_result = subprocess.run(
            ["docker", "build", "-t", image_name, "."], 
            cwd=self.temp_dir.name, 
            capture_output=True, 
            text=True,
            timeout=120,
        )
        if build_result.returncode != 0:
            raise TestExecutionError(f"Docker build failed: {build_result.stderr}")
            
        # Run container and mount the volume to extract the report
        # We mount the temp dir to /app so the generated report.json is saved to our local temp_dir
        run_result = subprocess.run(
            [
                "docker", "run", "--rm", "--network", "none",
                "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                "--pids-limit", "128", "--memory", "512m", "--cpus", "1",
                "-v", f"{self.temp_dir.name}:/app", image_name,
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # We don't raise an error if run_result != 0 because PyTest exits with 1 if tests fail
        # But if it's a structural docker run failure, we should catch it
        if "docker: Error response from daemon" in run_result.stderr:
            raise TestExecutionError(f"Docker run failed: {run_result.stderr}")
            
        # Cleanup image
        subprocess.run(["docker", "rmi", image_name], capture_output=True)
        
        # The pytest_runner expects the path to the test file to find the reports next to it
        return os.path.join(self.temp_dir.name, "test_generated.py")
        
    def cleanup(self):
        self.temp_dir.cleanup()
