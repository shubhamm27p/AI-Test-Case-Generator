import os
from ai_test_generator.config import load_config

def test_load_config(monkeypatch):
    monkeypatch.setenv("AI_TEST_GEN_MODE", "mock")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    config = load_config()
    assert config.mode == "mock"
    assert config.openai_api_key == "test-key"
