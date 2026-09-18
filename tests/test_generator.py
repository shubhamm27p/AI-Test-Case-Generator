"""
Tests for the TestGenerator class
"""

import pytest
from pathlib import Path
from ai_test_generator import TestGenerator


class TestTestGenerator:
    """Test suite for TestGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = TestGenerator()
    
    def test_initialization(self):
        """Test TestGenerator initialization."""
        assert self.generator is not None
        assert self.generator.config is not None
        assert self.generator.analyzer is not None
    
    def test_default_config(self):
        """Test default configuration."""
        config = self.generator._default_config()
        assert config['test_framework'] == 'pytest'
        assert config['include_edge_cases'] is True
        assert config['max_tests_per_function'] == 10
    
    def test_generate_valid_params(self):
        """Test parameter generation."""
        func_info = {
            'name': 'test_func',
            'parameters': [
                {'name': 'x', 'type': 'int'},
                {'name': 'y', 'type': 'str'},
                {'name': 'z', 'type': 'bool'}
            ]
        }
        
        params = self.generator._generate_valid_params(func_info)
        
        assert 'x' in params
        assert 'y' in params
        assert 'z' in params
        assert isinstance(params['x'], int)
        assert isinstance(params['y'], str)
        assert isinstance(params['z'], bool)
    
    def test_generate_basic_tests(self):
        """Test basic test case generation."""
        func_info = {
            'name': 'add',
            'parameters': [
                {'name': 'a', 'type': 'int'},
                {'name': 'b', 'type': 'int'}
            ]
        }
        
        tests = self.generator._generate_basic_tests(func_info)
        
        assert len(tests) > 0
        assert tests[0]['type'] == 'happy_path'
        assert tests[0]['function'] == 'add'


class TestCodeAnalyzer:
    """Test suite for CodeAnalyzer."""
    
    def test_analyze_simple_function(self):
        """Test analyzing a simple function."""
        from ai_test_generator.analyzer import CodeAnalyzer
        
        code = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(code)
        
        assert 'functions' in result
        assert len(result['functions']) == 1
        
        func = result['functions'][0]
        assert func['name'] == 'add'
        assert len(func['parameters']) == 2
        assert func['return_type'] == 'int'
    
    def test_analyze_function_with_exception(self):
        """Test analyzing function that raises exceptions."""
        from ai_test_generator.analyzer import CodeAnalyzer
        
        code = '''
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
'''
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(code)
        
        func = result['functions'][0]
        assert 'ValueError' in func['raises']


class TestEdgeCaseDetector:
    """Test suite for EdgeCaseDetector."""
    
    def test_boundary_value_tests(self):
        """Test boundary value detection."""
        from ai_test_generator.edge_case_detector import EdgeCaseDetector
        
        detector = EdgeCaseDetector()
        
        func_info = {
            'name': 'process',
            'parameters': [
                {'name': 'value', 'type': 'int'}
            ]
        }
        
        tests = detector._boundary_value_tests(func_info)
        
        assert len(tests) > 0
        # Should include tests for 0, -1, and max int
        assert any(t['params']['value'] == 0 for t in tests)
    
    def test_null_tests(self):
        """Test null value detection."""
        from ai_test_generator.edge_case_detector import EdgeCaseDetector
        
        detector = EdgeCaseDetector()
        
        func_info = {
            'name': 'process',
            'parameters': [
                {'name': 'data', 'type': 'str'}
            ]
        }
        
        tests = detector._null_tests(func_info)
        
        assert len(tests) > 0
        assert all(t['type'] == 'null_test' for t in tests)


class TestUserStoryParser:
    """Test suite for UserStoryParser."""
    
    def test_parse_standard_format(self):
        """Test parsing standard user story format."""
        from ai_test_generator.user_story_parser import UserStoryParser
        
        parser = UserStoryParser()
        story = "As a user, I want to login with email and password, so that I can access my account"
        
        result = parser.parse(story)
        
        assert result['role'] == 'user'
        assert 'login' in result['action'].lower()
        assert result['benefit'] is not None
    
    def test_generate_scenarios(self):
        """Test scenario generation."""
        from ai_test_generator.user_story_parser import UserStoryParser
        
        parser = UserStoryParser()
        story = "As a user, I want to login"
        
        parsed = parser.parse(story)
        scenarios = parser.generate_test_scenarios(parsed)
        
        assert len(scenarios) > 0
        assert any(s['type'] == 'happy_path' for s in scenarios)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
