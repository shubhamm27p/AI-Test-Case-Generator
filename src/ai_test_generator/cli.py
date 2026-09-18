import sys
import click
import os
from ai_test_generator.config import load_config
from ai_test_generator.generators.requirement_analyzer import RequirementAnalyzer
from ai_test_generator.analyzers.hf_classifier import HuggingFaceAnalyzer
from ai_test_generator.generators.test_case_generator import TestCaseGenerator
from ai_test_generator.generators.validation import TestCaseValidator
from ai_test_generator.generators.pytest_generator import PyTestGenerator
from ai_test_generator.execution.sandbox import Sandbox
from ai_test_generator.execution.pytest_runner import PyTestRunner
from ai_test_generator.reporting.reporters import Reporter
from rich.console import Console

console = Console()

@click.group()
def main():
    """AI-Powered Test Case Generator CLI"""
    pass

@main.command()
@click.argument('story')
@click.option('--code', '-c', help='Path to Python file containing code context')
@click.option('--output', '-o', default='tests/', help='Output directory')
def user_story(story, code, output):
    """Generate tests from a user story."""
    try:
        config = load_config()
        console.print(f"[bold blue]Running in {config.mode.upper()} mode[/bold blue]")
        
        requirement = story
        if os.path.isfile(story):
            with open(story, 'r') as f:
                requirement = f.read()

        code_context = ""
        if code and os.path.isfile(code):
            with open(code, 'r') as f:
                code_context = f.read()

        console.print("[yellow]Running Hugging Face NLP Quality Analysis...[/yellow]")
        hf_analyzer = HuggingFaceAnalyzer()
        hf_res = hf_analyzer.analyze_quality(requirement)
        console.print(f"[green]NLP Status: {hf_res.get('status')} (Score: {hf_res.get('score')})[/green]")

        console.print("[yellow]Analyzing requirement with LLM...[/yellow]")
        analyzer = RequirementAnalyzer()
        test_plan = analyzer.analyze_requirement(requirement, code_context)
        console.print("[green]Test plan generated![/green]")

        console.print("[yellow]Generating test cases...[/yellow]")
        tc_gen = TestCaseGenerator()
        raw_test_cases = tc_gen.generate_test_cases(requirement, test_plan, code_context)
        
        console.print("[yellow]Validating test cases...[/yellow]")
        validator = TestCaseValidator()
        test_cases = validator.validate(raw_test_cases)
        console.print(f"[green]Generated and validated {len(test_cases)} test cases![/green]")

        console.print("[yellow]Generating PyTest code...[/yellow]")
        py_gen = PyTestGenerator()
        pytest_code = py_gen.generate_code(test_cases, requirement, code_context)

        sandbox = Sandbox()
        test_file_path = sandbox.write_test_file(pytest_code)
        
        console.print("[yellow]Executing PyTest...[/yellow]")
        runner = PyTestRunner()
        result = runner.run_tests(test_file_path)
        
        console.print(f"[bold green]Execution Complete: {result.passed}/{result.total_tests} Passed[/bold green]")
        
        reporter = Reporter(output_dir=output)
        md_path = reporter.generate_markdown_report(result)
        console.print(f"Report generated at: {md_path}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

@main.command()
def ui():
    """Start the Streamlit UI."""
    import subprocess
    try:
        subprocess.run(["streamlit", "run", "src/ai_test_generator/ui/app.py"])
    except Exception as e:
        console.print(f"[bold red]Failed to start UI:[/bold red] {e}")

if __name__ == '__main__':
    main()
