import ast
import os
import tempfile
from pathlib import Path
from ..exceptions import TestExecutionError

class Sandbox:
    def __init__(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        
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

    def _sandbox_path(self, filename: str) -> str:
        sandbox_root = Path(self.temp_dir.name).resolve()
        file_path = (sandbox_root / filename).resolve()
        if file_path.parent != sandbox_root:
            raise TestExecutionError("Sandbox filename must stay inside the temporary directory.")
        return str(file_path)
        
    def validate_code(self, code: str):
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise TestExecutionError(f"Generated code has syntax errors: {e}")
            
        blocked_modules = {
            "builtins", "code", "ctypes", "glob", "importlib", "marshal",
            "multiprocessing", "os", "pathlib", "pickle", "resource", "shutil",
            "signal", "socket", "subprocess", "sys", "tempfile", "threading",
        }
        blocked_calls = {
            "__import__", "chmod", "chown", "compile", "eval", "exec", "input",
            "kill", "link", "makedirs", "mkdir", "open", "popen", "remove",
            "rename", "replace", "rmdir", "rmtree", "system", "unlink",
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_module = alias.name.split(".", 1)[0]
                    if root_module in blocked_modules:
                        raise TestExecutionError(f"Unsafe import detected: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                root_module = (node.module or "").split(".", 1)[0]
                if root_module in blocked_modules:
                    raise TestExecutionError(f"Unsafe import detected: {node.module}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in blocked_calls:
                        raise TestExecutionError(f"Unsafe function call detected: {node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in blocked_calls:
                        raise TestExecutionError(f"Unsafe attribute call detected: {node.func.attr}")
                        
    def cleanup(self):
        self.temp_dir.cleanup()
