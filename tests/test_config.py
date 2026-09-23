import os
from ai_test_generator.config import load_config, resolve_model_name

def test_load_config(monkeypatch):
    monkeypatch.setenv("AI_TEST_GEN_MODE", "mock")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    config = load_config()
    assert config.mode == "mock"
    assert config.openai_api_key == "test-key"

def test_load_config_model_alias(monkeypatch):
    monkeypatch.setenv("AI_TEST_GEN_MODE", "mock")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gemini-1.5-flash")
    config = load_config()
    assert config.openai_model == "gemini-3.6-flash"

def test_load_config_maps_deployed_gemini_model(monkeypatch):
    monkeypatch.setenv("AI_TEST_GEN_MODE", "mock")
    monkeypatch.setenv("OPENAI_MODEL", "gemini-3.6-flash")
    config = load_config()
    assert config.openai_model == "gemini-3.6-flash"

def test_resolve_model_name_strips_and_maps_alias():
    assert resolve_model_name(" gemini-3.6-flash ") == "gemini-3.6-flash"

def test_set_mode(monkeypatch):
    import pytest
    monkeypatch.setenv("AI_TEST_GEN_MODE", "mock")
    config = load_config()
    assert config.mode == "mock"
    
    config.set_mode("live")
    assert config.mode == "live"
    
    config.set_mode("TEST")
    assert config.mode == "test"
    
    with pytest.raises(ValueError, match="Invalid mode"):
        config.set_mode("invalid_mode")

