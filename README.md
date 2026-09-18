# AI Test Generator

An AI-powered testing platform that accepts natural-language software requirements and optional Python source code, then automatically generates:
1. Structured Test Plans
2. Comprehensive Test Cases (Positive, Negative, Boundary, Edge Case)
3. Executable PyTest Automation Code
4. Rich Execution Reports (JSON, Markdown, HTML)

## Features
- **Requirement Analysis**: Transforms vague requirements into a strict test strategy.
- **LLM Structured Output**: Uses OpenAI & LangChain to force AI responses into validated Pydantic models.
- **Safe Code Execution**: Parses generated Python code using AST to block dangerous imports before running them in a Sandbox.
- **Dynamic Streamlit UI**: User-friendly web interface for generating, viewing, and running tests.
- **Mock Mode**: Fully functional deterministic mock mode for local development, CI pipelines, and interviews without incurring API costs.
- **CI/CD Integration**: Pre-configured GitHub Actions to validate tests and demonstrate the pipeline.

## Architecture

1. **Requirement Analyzer**: LLM generates a `TestPlan` Pydantic model.
2. **TestCase Generator**: LLM generates a `TestSuite` (list of `TestCase`) referencing the `TestPlan`.
3. **PyTest Generator**: LLM generates executable PyTest code.
4. **Execution Sandbox**: AST analysis validates code safety, saves it to a temp dir, and runs PyTest in a subprocess.
5. **Reporting Module**: Parses `pytest-json-report` outputs into JSON, Markdown, and HTML reports.

## Technology Stack
- **Python 3.8+**
- **OpenAI API & LangChain** (Core AI orchestration)
- **Pydantic** (Validation & Structured Outputs)
- **PyTest** (Test execution framework)
- **Streamlit** (Web UI)
- **GitHub Actions** (CI/CD)

## Installation

```bash
git clone https://github.com/Naysrania18/ai-test-generator.git
cd ai-test-generator

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Environment Setup
Create a `.env` file in the root directory (refer to `.env.example`):
```ini
OPENAI_API_KEY=your_actual_key_here
OPENAI_MODEL=gpt-4o-mini
AI_TEST_GEN_MODE=live
EXECUTION_TIMEOUT=30
```
> **Note**: For interviews or local CI runs without an API key, set `AI_TEST_GEN_MODE=mock`.

## Usage

### 1. Web UI (Streamlit)
```bash
ai-test-gen ui
```
Alternatively:
```bash
streamlit run src/ai_test_generator/ui/app.py
```

### 2. Command Line Interface
```bash
# Run the complete pipeline (generation -> execution -> reporting)
ai-test-gen user-story "Users can register an account using email and password" --output tests/reports
```

## Security Limitations
- **AST Checks**: The execution sandbox prevents obvious dangerous imports (`os`, `subprocess`, `exec`) but does not provide complete OS-level isolation (e.g., Docker). For enterprise usage, containerize the executor.

## Demo / Mock Mode
If you want to evaluate the architecture without an OpenAI key, switch to mock mode in `.env`:
`AI_TEST_GEN_MODE=mock`
This will immediately return deterministic, pre-configured test plans and code that can still be executed.
