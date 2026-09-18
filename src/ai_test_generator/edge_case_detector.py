"""
Edge Case Detector Module
Identifies potential edge cases and boundary conditions.
"""

from typing import Dict, List, Any


class EdgeCaseDetector:
    """
    Detects edge cases based on function signatures and types.
    """
    
    def __init__(self):
        self.type_edge_cases = {
            'int': [0, -1, 1, 2**31-1, -2**31],
            'float': [0.0, -1.0, 1.0, float('inf'), float('-inf'), float('nan')],
            'str': ['', ' ', 'a', 'A' * 1000],
            'list': [[], [None], [1, 2, 3]],
            'dict': [{}, {'key': 'value'}],
            'bool': [True, False],
        }
    
    def detect_edge_cases(self, func_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect edge cases for a function.
        
        Args:
            func_info: Function information from analyzer
            
        Returns:
            List of edge case test specifications
        """
        edge_cases = []
        
        # Boundary value tests
        edge_cases.extend(self._boundary_value_tests(func_info))
        
        # Type-specific edge cases
        edge_cases.extend(self._type_edge_cases(func_info))
        
        # Exception-based tests
        edge_cases.extend(self._exception_tests(func_info))
        
        # Empty/null tests
        edge_cases.extend(self._null_tests(func_info))
        
        # Size/length tests
        edge_cases.extend(self._size_tests(func_info))
        
        return edge_cases
    
    def _boundary_value_tests(self, func_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate boundary value tests."""
        tests = []
        
        for param in func_info.get('parameters', []):
            param_type = param.get('type', 'Any')
            param_name = param['name']
            
            if param_type == 'int':
                # Test with boundary values
                tests.append({
                    'type': 'boundary_value',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with zero for {param_name}",
                    'params': {param_name: 0},
                    'expected': 'boundary_check'
                })
                
                tests.append({
                    'type': 'boundary_value',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with negative value for {param_name}",
                    'params': {param_name: -1},
                    'expected': 'boundary_check'
                })
                
                tests.append({
                    'type': 'boundary_value',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with max int for {param_name}",
                    'params': {param_name: 2**31 - 1},
                    'expected': 'boundary_check'
                })
            
            elif param_type == 'float':
                tests.append({
                    'type': 'boundary_value',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with infinity for {param_name}",
                    'params': {param_name: float('inf')},
                    'expected': 'boundary_check'
                })
                
                tests.append({
                    'type': 'boundary_value',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with NaN for {param_name}",
                    'params': {param_name: float('nan')},
                    'expected': 'boundary_check'
                })
        
        return tests
    
    def _type_edge_cases(self, func_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate type-specific edge cases."""
        tests = []
        
        for param in func_info.get('parameters', []):
            param_type = param.get('type', 'Any')
            param_name = param['name']
            
            # Get edge cases for this type
            edge_values = self.type_edge_cases.get(param_type, [])
            
            for value in edge_values:
                tests.append({
                    'type': 'type_edge_case',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with edge case value {repr(value)} for {param_name}",
                    'params': {param_name: value},
                    'expected': 'edge_case_handling'
                })
        
        return tests
    
    def _exception_tests(self, func_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tests for raised exceptions."""
        tests = []
        
        for exception in func_info.get('raises', []):
            tests.append({
                'type': 'exception_test',
                'function': func_info['name'],
                'description': f"Test {func_info['name']} raises {exception}",
                'params': self._get_exception_trigger_params(func_info, exception),
                'expected': f'raises_{exception}'
            })
        
        return tests
    
    def _get_exception_trigger_params(
        self,
        func_info: Dict[str, Any],
        exception: str
    ) -> Dict[str, Any]:
        """Generate parameters that should trigger the exception."""
        params = {}
        
        # Common exception triggers
        if exception == 'ValueError':
            for param in func_info.get('parameters', []):
                param_type = param.get('type', 'Any')
                if param_type == 'int':
                    params[param['name']] = -1
                elif param_type == 'str':
                    params[param['name']] = ''
        
        elif exception == 'TypeError':
            for param in func_info.get('parameters', []):
                params[param['name']] = None
        
        elif exception == 'IndexError':
            for param in func_info.get('parameters', []):
                if 'list' in param.get('type', '').lower():
                    params[param['name']] = []
        
        elif exception == 'KeyError':
            for param in func_info.get('parameters', []):
                if 'dict' in param.get('type', '').lower():
                    params[param['name']] = {}
        
        return params
    
    def _null_tests(self, func_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate null/None tests."""
        tests = []
        
        for param in func_info.get('parameters', []):
            param_name = param['name']
            
            tests.append({
                'type': 'null_test',
                'function': func_info['name'],
                'description': f"Test {func_info['name']} with None for {param_name}",
                'params': {param_name: None},
                'expected': 'null_handling'
            })
        
        return tests
    
    def _size_tests(self, func_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tests for size/length edge cases."""
        tests = []
        
        for param in func_info.get('parameters', []):
            param_type = param.get('type', 'Any')
            param_name = param['name']
            
            if param_type == 'str':
                # Empty string
                tests.append({
                    'type': 'size_test',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with empty string for {param_name}",
                    'params': {param_name: ''},
                    'expected': 'empty_handling'
                })
                
                # Very long string
                tests.append({
                    'type': 'size_test',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with very long string for {param_name}",
                    'params': {param_name: 'A' * 10000},
                    'expected': 'large_input_handling'
                })
            
            elif param_type == 'list' or 'List' in param_type:
                # Empty list
                tests.append({
                    'type': 'size_test',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with empty list for {param_name}",
                    'params': {param_name: []},
                    'expected': 'empty_handling'
                })
                
                # Large list
                tests.append({
                    'type': 'size_test',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with large list for {param_name}",
                    'params': {param_name: list(range(10000))},
                    'expected': 'large_input_handling'
                })
            
            elif param_type == 'dict' or 'Dict' in param_type:
                # Empty dict
                tests.append({
                    'type': 'size_test',
                    'function': func_info['name'],
                    'description': f"Test {func_info['name']} with empty dict for {param_name}",
                    'params': {param_name: {}},
                    'expected': 'empty_handling'
                })
        
        return tests
    
    def analyze_return_value_edges(self, func_info: Dict[str, Any]) -> List[str]:
        """
        Analyze potential edge cases in return values.
        
        Args:
            func_info: Function information
            
        Returns:
            List of edge case descriptions
        """
        edges = []
        return_type = func_info.get('return_type', 'Any')
        
        if return_type == 'int':
            edges.extend(['zero', 'negative', 'maximum'])
        elif return_type == 'str':
            edges.extend(['empty_string', 'single_char', 'very_long'])
        elif return_type == 'list' or 'List' in return_type:
            edges.extend(['empty_list', 'single_element', 'many_elements'])
        elif return_type == 'bool':
            edges.extend(['true', 'false'])
        elif return_type == 'None':
            edges.extend(['none'])
        
        return edges
