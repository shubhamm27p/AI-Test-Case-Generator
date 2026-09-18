# AI Test Generator - Interview Guide

This guide explains the key concepts and technical decisions for the AI Test Generator.

## What is this project?
An AI-powered testing platform that accepts natural-language software requirements and Python source code, and dynamically generates test plans, test cases, executable PyTest automation code, and execution reports.

## Why did you build it?
To solve the bottleneck of manual test case creation and reduce the time spent bridging requirements and test automation, proving that LLMs can structurally enhance QA workflows safely.

## How does LLM generation work?
We use the OpenAI API to analyze requirements. Instead of relying on raw text parsing, we use LangChain and OpenAI's structured outputs (`with_structured_output`), mapping LLM outputs directly to strict Pydantic data models (TestPlan, TestCase).

## Why OpenAI & LangChain?
OpenAI provides state-of-the-art instruction following and reasoning. LangChain allows for clean orchestration, structured extraction, and prompt templating, decoupling the logic from raw API requests.

## Why PyTest & GitHub Actions?
PyTest is the industry standard for Python testing. It provides rich reporting (via `pytest-json-report`). GitHub Actions provides seamless CI/CD automation to run tests on every commit.

## How are AI hallucinations handled?
By forcing structured Pydantic models. We ensure every output matches expected schema formats. The system explicitly separates test generation from execution to validate AST integrity before ever running code.

## How is generated code made safer?
We utilize Python's `ast` module to statically analyze generated code for dangerous imports (like `os`, `subprocess`) or function calls (`eval`, `exec`) before saving it to a temporary execution sandbox. We execute it in an isolated subprocess with strict timeouts.
