import json
import os
from html import escape
from pathlib import Path
from typing import Dict, Any
from ..models.test_result import ExecutionResult

class Reporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _report_path(self, filename: str) -> str:
        output_root = Path(self.output_dir).resolve()
        report_path = (output_root / filename).resolve()
        if report_path.parent != output_root:
            raise ValueError("Report filename must stay inside the output directory.")
        return str(report_path)
        
    def generate_json_report(self, result: ExecutionResult, filename: str = "report.json") -> str:
        filepath = self._report_path(filename)
        with open(filepath, "w") as f:
            f.write(result.model_dump_json(indent=2))
        return filepath
        
    def generate_markdown_report(self, result: ExecutionResult, filename: str = "report.md") -> str:
        filepath = self._report_path(filename)
        
        lines = [
            "# AI Test Generation Report",
            "",
            "## Summary",
            f"- **Total Tests:** {result.total_tests}",
            f"- **Passed:** {result.passed}",
            f"- **Failed:** {result.failed}",
            f"- **Skipped:** {result.skipped}",
            f"- **Errors:** {result.errors}",
            f"- **Pass Percentage:** {result.pass_percentage:.2f}%",
            f"- **Duration:** {result.duration:.2f}s",
            "",
            "## Test Details",
            ""
        ]
        
        for t in result.tests:
            lines.append(f"### {t.title}")
            lines.append(f"- **Status:** {t.status.upper()}")
            lines.append(f"- **Duration:** {t.duration:.2f}s")
            if t.error_message:
                lines.append(f"- **Error:**\n```\n{t.error_message}\n```")
            lines.append("")
            
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
            
        return filepath
        
    def generate_html_report(self, result: ExecutionResult, filename: str = "report.html") -> str:
        filepath = self._report_path(filename)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
<title>AI Test Generation Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
.summary {{ background: #f4f4f4; padding: 15px; border-radius: 5px; }}
.test-passed {{ color: green; }}
.test-failed {{ color: red; }}
.test-skipped {{ color: orange; }}
</style>
</head>
<body>
    <h1>AI Test Generation Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {result.total_tests}</p>
        <p>Passed: {result.passed}</p>
        <p>Failed: {result.failed}</p>
        <p>Skipped: {result.skipped}</p>
        <p>Errors: {result.errors}</p>
        <p>Pass Percentage: {result.pass_percentage:.2f}%</p>
        <p>Duration: {result.duration:.2f}s</p>
    </div>
    <h2>Test Details</h2>
"""
        for t in result.tests:
            status = escape(str(t.status))
            status_class = f"test-{status}"
            html += f"<h3>{escape(str(t.title))} (<span class='{status_class}'>{status.upper()}</span>)</h3>"
            html += f"<p>Duration: {t.duration:.2f}s</p>"
            if t.error_message:
                html += f"<pre style='background:#eee;padding:10px;'>{escape(str(t.error_message))}</pre>"
                
        html += "</body></html>"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
            
        return filepath
