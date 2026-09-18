"""
Main Test Generator Module
Orchestrates the test generation process.
"""

import os
import ast
from typing import List, Dict, Optional, Any
from pathlib import Path

from .analyzer import CodeAnalyzer
from .edge_case_detector import EdgeCaseDetector
from .ml_model import TestCaseModel
from .templates import TestTemplate
from .user_story_parser import UserStoryParser


class TestGenerator:
    __test__ = False
    """
    Main class for generating test cases from code and user stories.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Test Generator.
        
        Args:
            model_path: Path to the trained ML model
            config: Configuration dictionary
        """
        self.config = config or self._default_config()
        self.analyzer = CodeAnalyzer()
        self.edge_detector = EdgeCaseDetector()
        self.model = TestCaseModel(model_path)
        self.template = TestTemplate()
        self.user_story_parser = UserStoryParser()
        
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'test_framework': 'pytest',
            'include_edge_cases': True,
            'include_mocks': True,
            'max_tests_per_function': 10,
            'confidence_threshold': 0.7,
            'output_directory': 'tests/',
            'file_naming': 'test_{filename}.py'
        }
    
    def analyze_file(
        self,
        file_path: str,
        include_edge_cases: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Analyze a Python file and generate test case specifications.
        
        Args:
            file_path: Path to the Python file to analyze
            include_edge_cases: Whether to include edge case detection
            
        Returns:
            List of test case specifications
        """
        # Parse the file
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        # Analyze code structure
        analysis_result = self.analyzer.analyze(source_code)
        
        test_cases = []
        
        # Generate test cases for each function
        for func_info in analysis_result['functions']:
            # Generate basic test cases
            basic_tests = self._generate_basic_tests(func_info)
            test_cases.extend(basic_tests)
            
            # Generate edge case tests if enabled
            if include_edge_cases:
                edge_tests = self.edge_detector.detect_edge_cases(func_info)
                test_cases.extend(edge_tests)
            
            # Use ML model to suggest additional tests
            ml_suggested = self.model.predict_test_cases(func_info)
            test_cases.extend(ml_suggested)
        
        return test_cases
    
    def _generate_basic_tests(
        self,
        func_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate basic test cases for a function.
        
        Args:
            func_info: Function information from analyzer
            
        Returns:
            List of basic test cases
        """
        tests = []
        
        # Generate happy path test
        tests.append({
            'type': 'happy_path',
            'function': func_info['name'],
            'description': f"Test {func_info['name']} with valid inputs",
            'params': self._generate_valid_params(func_info),
            'expected': 'success'
        })
        
        # Generate null/None tests for optional parameters
        for param in func_info.get('parameters', []):
            if param.get('optional', False):
                tests.append({
                    'type': 'null_check',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with None for {param['name']}",
                    'params': {param['name']: None},
                    'expected': 'handle_gracefully'
                })
        
        return tests
    
    def _generate_valid_params(
        self,
        func_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate valid parameter values based on type hints."""
        params = {}
        
        for param in func_info.get('parameters', []):
            param_type = param.get('type', 'Any')
            
            if param_type == 'int':
                params[param['name']] = 1
            elif param_type == 'float':
                params[param['name']] = 1.0
            elif param_type == 'str':
                params[param['name']] = "test"
            elif param_type == 'bool':
                params[param['name']] = True
            elif param_type == 'list':
                params[param['name']] = []
            elif param_type == 'dict':
                params[param['name']] = {}
            else:
                params[param['name']] = None
        
        return params
    
    def generate_test_file(
        self,
        source_file: str,
        output_path: Optional[str] = None,
        include_edge_cases: bool = True
    ) -> str:
        """
        Generate a complete test file from a source file.
        
        Args:
            source_file: Path to the source Python file
            output_path: Path for the output test file
            include_edge_cases: Whether to include edge case tests
            
        Returns:
            Path to the generated test file
        """
        # Analyze the file
        test_cases = self.analyze_file(source_file, include_edge_cases)
        
        # Generate test code
        test_code = self.template.render(
            source_file=source_file,
            test_cases=test_cases,
            framework=self.config['test_framework']
        )
        
        # Determine output path
        if output_path is None:
            source_path = Path(source_file)
            filename = self.config['file_naming'].format(
                filename=source_path.stem
            )
            output_path = Path(self.config['output_directory']) / filename
        
        # Create output directory if it doesn't exist
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write test file
        with open(output_path, 'w') as f:
            f.write(test_code)
        
        return str(output_path)
    
    def generate_from_user_story(
        self,
        user_story: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate test cases from a user story.
        
        Args:
            user_story: User story text
            output_path: Path for the output test file
            
        Returns:
            Path to the generated test file
        """
        # Parse user story
        parsed_story = self.user_story_parser.parse(user_story)
        
        # Generate test scenarios
        test_scenarios = self.user_story_parser.generate_test_scenarios(
            parsed_story
        )
        
        # Generate test code
        test_code = self.template.render_user_story_tests(
            user_story=user_story,
            scenarios=test_scenarios,
            framework=self.config['test_framework']
        )
        
        # Write to file
        if output_path is None:
            output_path = Path(self.config['output_directory']) / 'test_user_story.py'
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(test_code)
        
        return str(output_path)
    
    def analyze_project(
        self,
        project_path: str,
        output_dir: str = 'tests/',
        file_patterns: List[str] = None
    ) -> Dict[str, str]:
        """
        Analyze an entire project and generate tests.
        
        Args:
            project_path: Root path of the project
            output_dir: Directory for output test files
            file_patterns: List of file patterns to match (e.g., ['*.py'])
            
        Returns:
            Dictionary mapping source files to generated test files
        """
        if file_patterns is None:
            file_patterns = ['*.py']
        
        project_path = Path(project_path)
        results = {}
        
        # Find all Python files
        for pattern in file_patterns:
            for source_file in project_path.rglob(pattern):
                # Skip test files and __init__.py
                if 'test' in source_file.name or source_file.name == '__init__.py':
                    continue
                
                try:
                    # Generate test file
                    relative_path = source_file.relative_to(project_path)
                    output_path = Path(output_dir) / f"test_{relative_path}"
                    
                    test_file = self.generate_test_file(
                        str(source_file),
                        str(output_path)
                    )
                    
                    results[str(source_file)] = test_file
                    
                except Exception as e:
                    print(f"Error processing {source_file}: {e}")
        
        return results
