# Security Audit Report

Date: 2026-09-14
Scope: source code, configuration, execution sandboxes, reporting, tests, and deployment readiness.

## Executive Summary

The project is suitable for continued deployment preparation after the fixes listed below. The focused security probes, full configured test suite, and Python compilation pass. The application executes generated Python code, so it must be deployed with the Docker sandbox enabled and behind authentication; the local AST sandbox is only defense-in-depth and is not an OS-level isolation boundary.

## Findings Resolved

### 1. Generated code bypassed validation in Docker mode
Severity: High

`DockerSandbox` wrote test and application code without applying the AST safety checks. Generated code could therefore execute imports and calls that the local sandbox rejects.

Resolution: DockerSandbox now reuses Sandbox validation before writing files.

### 2. Sandbox path traversal
Severity: High

Application filenames were joined directly to the temporary directory. A caller could provide a path such as `../file.py` and write outside the sandbox.

Resolution: sandbox and report paths are resolved and required to remain directly under their configured root directory.

### 3. Unsafe container execution defaults
Severity: High

Docker execution had unrestricted network access, Linux capabilities, process creation, memory, and CPU use.

Resolution: Docker runs now use no network, drop all capabilities, disable privilege escalation, and apply PID, memory, CPU, build, and test timeouts.

### 4. HTML report injection
Severity: Medium

Test titles, statuses, and error messages were inserted into HTML without escaping. Generated or failing test content could inject markup or script when the report was opened.

Resolution: dynamic report values are HTML-escaped.

### 5. Runtime configuration could be overwritten by `.env`
Severity: Medium

`load_dotenv(..., override=True)` allowed a local `.env` to override environment variables injected by a deployment platform and test harness.

Resolution: environment variables now take precedence over `.env` values.

### 6. Pytest configuration was ignored
Severity: Medium

`pytest.ini` used `[tool:pytest]` instead of `[pytest]`, causing pytest to collect illustrative generated examples outside `tests/` and report failures unrelated to the configured suite.

Resolution: the section header is corrected. The configured suite now collects only `tests/`.

## Verification

- `venv\\Scripts\\python.exe -m pytest -q`: 13 passed.
- `venv\\Scripts\\python.exe -m compileall -q src tests examples`: passed.
- Focused security probes: passed for blocked imports/calls, Docker validation, path traversal, and HTML escaping.
- `git diff --check`: passed.
- Flake8: reports extensive pre-existing style violations across the repository; these are not security fixes and were left unchanged.
- Mypy: blocked by the available Python 3.14 environment conflicting with the project's Python 3.8 target and installed NumPy stubs.

## Deployment Requirements

1. Revoke and rotate the API key currently present in the local `.env`. It was not committed because `.env` is ignored, but it must be treated as exposed. Do not place real secrets in `.env.example` or source control.
2. Set `SANDBOX_TYPE=docker` in production. Do not expose the local sandbox to untrusted generated code.
3. Put Streamlit behind an authenticated reverse proxy or identity provider. The application has no built-in user authentication or authorization layer.
4. Use a dedicated Docker host or restricted runtime. The Docker sandbox is defense-in-depth, not a complete substitute for a separate worker, VM, or hardened container service.
5. Pin dependency versions and run a vulnerability scanner such as `pip-audit` in CI before deployment. Current requirement ranges permit dependency drift.
6. Configure resource limits at the host/platform level as well as in Docker, and set a non-root container user where the deployment environment supports it.
7. Ensure logs and error responses do not contain API keys or other user-provided secrets.
8. Use HTTPS for any configured `OPENAI_BASE_URL` outside a trusted local development endpoint.

## Residual Risk

The AST validator is a denylist and cannot prove that arbitrary Python is safe. Python generated from untrusted input should never be executed in the local sandbox on a production service. Docker image builds and the Docker daemon remain privileged operational dependencies and require host-level hardening.
