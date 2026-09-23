import sys
from pathlib import Path

# Ensure 'src' is in sys.path so 'ai_test_generator' can be imported in hosted environments like Streamlit Cloud
src_path = str(Path(__file__).resolve().parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import os
import json
import streamlit as st
from ai_test_generator.config import load_config
from ai_test_generator.llm.client import LLMClient
from ai_test_generator.generators.requirement_analyzer import RequirementAnalyzer
from ai_test_generator.generators.test_case_generator import TestCaseGenerator
from ai_test_generator.generators.pytest_generator import PyTestGenerator
from ai_test_generator.generators.app_generator import AppCodeGenerator
from ai_test_generator.execution.sandbox import Sandbox
from ai_test_generator.execution.docker_sandbox import DockerSandbox
from ai_test_generator.execution.pytest_runner import PyTestRunner
from ai_test_generator.reporting.reporters import Reporter

def main():
    st.set_page_config(page_title="AI Test Generator", layout="wide", initial_sidebar_state="expanded")
    
    st.sidebar.title("🧪 AI Test Generator")
    config = load_config()
    
    if config.mode != "mock" and not config.openai_api_key:
        st.error("OpenAI API key is not configured. Add OPENAI_API_KEY to your .env file or Streamlit secrets.")
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("Configuration")
    st.sidebar.write(f"**Mode:** `{config.mode.upper()}`")
    
    selected_model = st.sidebar.text_input(
        "Model",
        value=config.openai_model,
        help="Specify the model name (e.g. gemini-3.6-flash, gpt-4o-mini). Deprecated Gemini models are automatically mapped."
    )
    if selected_model and selected_model.strip():
        config.openai_model = selected_model.strip()

    st.sidebar.write(f"**Sandbox:** `{config.sandbox_type.upper()}`")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Testing Features")
    include_api = st.sidebar.checkbox("Include API Testing Scenarios", value=False)
    include_perf = st.sidebar.checkbox("Include Performance Scenarios", value=False)
    generate_tdd = st.sidebar.checkbox("Generate App Code (TDD Mode)", value=False, help="Automatically write backend implementation code so tests pass.")

    # Initialize State
    for key in ["test_plan", "test_cases", "pytest_code", "app_code", "execution_result"]:
        if key not in st.session_state:
            st.session_state[key] = None

    st.title("Test Generation Dashboard")
    st.markdown("Generate comprehensive Test Plans, Test Cases, and PyTest code from user stories.")
    
    tabs = st.tabs(["📝 Input", "📋 Test Plan", "✅ Test Cases", "💻 Test Code", "🚀 App Code", "📊 Execution"])
    tab_input, tab_plan, tab_cases, tab_code, tab_app, tab_report = tabs

    with tab_input:
        st.subheader("Provide Requirements")
        col1, col2 = st.columns(2)
        with col1:
            requirement = st.text_area("Software Requirement / User Story*", height=200, placeholder="As a user, I want to...")
        with col2:
            code_context = st.text_area("Optional Python Code Context", height=200, placeholder="def login(email, password):\n...")

        if st.button("🚀 Generate Everything", type="primary", use_container_width=True):
            if not requirement.strip():
                st.error("Please enter a requirement.")
                return

            with st.status("Generating Assets...", expanded=True) as status:
                llm_client = LLMClient(config=config)
                st.write("🔍 Analyzing Requirement...")
                analyzer = RequirementAnalyzer(llm_client=llm_client)
                try:
                    st.session_state.test_plan = analyzer.analyze_requirement(requirement, code_context, include_api, include_perf)
                except Exception as e:
                    st.error(f"Error generating Test Plan: {e}")
                    status.update(label="Failed", state="error")
                    return
                
                if generate_tdd:
                    st.write("🚀 Generating Implementation (TDD)...")
                    app_gen = AppCodeGenerator(llm_client=llm_client)
                    try:
                        st.session_state.app_code = app_gen.generate_app_code(requirement, st.session_state.test_plan)
                    except Exception as e:
                        st.error(f"Error generating App Code: {e}")
                        status.update(label="Failed", state="error")
                        return
                        
                st.write("📝 Generating Test Cases & Code Snippets...")
                tc_gen = TestCaseGenerator(llm_client=llm_client)
                try:
                    st.session_state.test_cases = tc_gen.generate_test_cases(requirement, st.session_state.test_plan, code_context, include_api, include_perf)
                except Exception as e:
                    st.error(f"Error generating Test Cases: {e}")
                    status.update(label="Failed", state="error")
                    return
                
                st.write("💻 Compiling PyTest Code...")
                py_gen = PyTestGenerator(llm_client=llm_client)
                try:
                    st.session_state.pytest_code = py_gen.generate_code(st.session_state.test_cases, requirement, code_context)
                except Exception as e:
                    st.error(f"Error generating PyTest code: {e}")
                    status.update(label="Failed", state="error")
                    return
                    
                status.update(label="Generation Complete!", state="complete", expanded=False)

    with tab_plan:
        if st.session_state.test_plan:
            st.subheader(st.session_state.test_plan.feature_name)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Objective:** {st.session_state.test_plan.objective}")
                st.markdown(f"**Scope:** {st.session_state.test_plan.scope}")
                st.markdown(f"**Approach:** {st.session_state.test_plan.testing_approach}")
            with col2:
                st.markdown("**Test Types:**")
                for t in st.session_state.test_plan.test_types:
                    st.markdown(f"- {t}")
                if st.session_state.test_plan.api_testing_strategy:
                    st.markdown(f"**API Strategy:** {st.session_state.test_plan.api_testing_strategy}")
                if st.session_state.test_plan.performance_criteria:
                    st.markdown(f"**Performance Criteria:** {st.session_state.test_plan.performance_criteria}")
            
            st.download_button("Download Test Plan JSON", data=st.session_state.test_plan.model_dump_json(indent=2), file_name="test_plan.json", mime="application/json")
        else:
            st.info("Generate a test plan to view it here.")

    with tab_cases:
        if st.session_state.test_cases:
            st.subheader(f"Generated {len(st.session_state.test_cases)} Test Cases")
            for tc in st.session_state.test_cases:
                color = "green" if tc.test_type.lower() == "positive" else "red" if tc.test_type.lower() == "negative" else "blue"
                with st.expander(f"{tc.test_case_id}: {tc.title} (:{color}[{tc.test_type}])"):
                    st.markdown(f"**Description:** {tc.description}")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Steps:**")
                        for i, step in enumerate(tc.steps):
                            st.markdown(f"{i+1}. {step}")
                    with c2:
                        if tc.api_endpoint:
                            st.markdown(f"**API Endpoint:** `{tc.api_endpoint}`")
                        if tc.performance_threshold:
                            st.markdown(f"**Performance Threshold:** `{tc.performance_threshold}`")
                        st.markdown(f"**Expected Result:** {tc.expected_result}")
                    
                    if tc.code_snippet:
                        st.markdown("**Generated Code Snippet:**")
                        st.code(tc.code_snippet, language="python")

            test_cases_json = json.dumps([t.model_dump() for t in st.session_state.test_cases], indent=2)
            st.download_button("Download Test Cases JSON", data=test_cases_json, file_name="test_cases.json", mime="application/json")
        else:
            st.info("Generate test cases to view them here.")

    with tab_code:
        if st.session_state.pytest_code:
            st.code(st.session_state.pytest_code, language="python")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.download_button("Download PyTest Code", data=st.session_state.pytest_code, file_name="test_generated.py", mime="text/x-python")
            with col2:
                if st.button("▶️ Execute Tests in Sandbox", use_container_width=True):
                    with st.spinner("Executing Tests..."):
                        sandbox = DockerSandbox() if config.sandbox_type == "docker" else Sandbox()
                        runner = PyTestRunner()
                        try:
                            # Write application code to sandbox if we are in TDD mode
                            if generate_tdd and st.session_state.app_code:
                                sandbox.write_app_file(st.session_state.app_code, "app.py")
                            
                            # Write the test file
                            test_file_path = sandbox.write_test_file(st.session_state.pytest_code)
                            
                            # If using docker sandbox, execute tests within it first
                            if config.sandbox_type == "docker":
                                sandbox.execute_tests()
                                
                            st.session_state.execution_result = runner.run_tests(test_file_path)
                            st.success("Tests Executed Successfully! View the Execution tab.")
                        except Exception as e:
                            st.error(f"Execution Error: {e}")
                        finally:
                            sandbox.cleanup()
        else:
            st.info("Generate PyTest code to view it here.")
            
    with tab_app:
        if st.session_state.app_code:
            st.code(st.session_state.app_code, language="python")
            st.download_button("Download Application Code", data=st.session_state.app_code, file_name="app.py", mime="text/x-python")
        else:
            if generate_tdd:
                st.info("Generate TDD code to view it here.")
            else:
                st.warning("Enable 'Generate App Code (TDD Mode)' in the sidebar to use this feature.")

    with tab_report:
        if st.session_state.execution_result:
            res = st.session_state.execution_result
            st.subheader("Test Execution Report")
            
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Total Tests", res.total_tests)
            mc2.metric("Passed", res.passed)
            mc3.metric("Failed", res.failed)
            mc4.metric("Pass Rate", f"{res.pass_percentage:.1f}%")
            
            st.markdown("---")
            for t in res.tests:
                status_color = "green" if t.status == "passed" else "red" if t.status == "failed" else "orange"
                st.markdown(f"**{t.title}** - :{status_color}[{t.status.upper()}] ({t.duration:.2f}s)")
                if t.error_message:
                    st.code(t.error_message)
                    
            reporter = Reporter(output_dir="tests/reports")
            md_path = reporter.generate_markdown_report(res)
            html_path = reporter.generate_html_report(res)
            
            with open(md_path, "r", encoding="utf-8") as f:
                st.download_button("Download Markdown Report", data=f.read(), file_name="report.md", mime="text/markdown")
            with open(html_path, "r", encoding="utf-8") as f:
                st.download_button("Download HTML Report", data=f.read(), file_name="report.html", mime="text/html")
        else:
            st.info("Execute tests to view the report here.")

if __name__ == "__main__":
    main()
