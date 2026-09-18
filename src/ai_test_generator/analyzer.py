"""
Code Analyzer Module
Analyzes Python code using AST to extract function signatures and metadata.
"""

import ast
from typing import Dict, List, Any, Optional


class CodeAnalyzer:
    """
    Analyzes Python source code to extract function information.
    """
    
    def __init__(self):
        self.tree = None
        self.source = None
    
    def analyze(self, source_code: str) -> Dict[str, Any]:
        """
        Analyze Python source code.
        
        Args:
            source_code: Python source code as string
            
        Returns:
            Dictionary containing analysis results
        """
        self.source = source_code
        self.tree = ast.parse(source_code)
        
        result = {
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 0
        }
        
        # Extract functions
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._analyze_function(node)
                result['functions'].append(func_info)
            elif isinstance(node, ast.ClassDef):
                class_info = self._analyze_class(node)
                result['classes'].append(class_info)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                import_info = self._analyze_import(node)
                result['imports'].append(import_info)
        
        result['complexity'] = self._calculate_complexity(self.tree)
        
        return result
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """
        Extract information from a function definition.
        
        Args:
            node: AST FunctionDef node
            
        Returns:
            Dictionary with function information
        """
        func_info = {
            'name': node.name,
            'parameters': [],
            'return_type': None,
            'docstring': ast.get_docstring(node),
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
            'line_number': node.lineno,
            'complexity': self._calculate_complexity(node)
        }
        
        # Extract parameters
        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'type': self._get_type_annotation(arg),
                'optional': False
            }
            func_info['parameters'].append(param_info)
        
        # Mark optional parameters (those with defaults)
        num_defaults = len(node.args.defaults)
        if num_defaults > 0:
            for i in range(num_defaults):
                func_info['parameters'][-(i+1)]['optional'] = True
                func_info['parameters'][-(i+1)]['default'] = self._get_default_value(
                    node.args.defaults[-(i+1)]
                )
        
        # Extract return type
        if node.returns:
            func_info['return_type'] = self._get_type_annotation_from_node(node.returns)
        
        # Analyze function body for exception handling
        func_info['raises'] = self._find_exceptions(node)
        func_info['has_assertions'] = self._has_assertions(node)
        
        return func_info
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """
        Extract information from a class definition.
        
        Args:
            node: AST ClassDef node
            
        Returns:
            Dictionary with class information
        """
        class_info = {
            'name': node.name,
            'bases': [self._get_name(base) for base in node.bases],
            'methods': [],
            'docstring': ast.get_docstring(node),
            'line_number': node.lineno
        }
        
        # Extract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._analyze_function(item)
                method_info['is_method'] = True
                method_info['is_static'] = 'staticmethod' in method_info['decorators']
                method_info['is_class_method'] = 'classmethod' in method_info['decorators']
                class_info['methods'].append(method_info)
        
        return class_info
    
    def _analyze_import(self, node: ast.Import | ast.ImportFrom) -> Dict[str, Any]:
        """Extract import information."""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'modules': [alias.name for alias in node.names]
            }
        else:  # ImportFrom
            return {
                'type': 'from_import',
                'module': node.module,
                'names': [alias.name for alias in node.names]
            }
    
    def _get_type_annotation(self, arg: ast.arg) -> str:
        """Get type annotation from argument."""
        if arg.annotation:
            return self._get_type_annotation_from_node(arg.annotation)
        return 'Any'
    
    def _get_type_annotation_from_node(self, node: ast.AST) -> str:
        """Convert AST type annotation to string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Subscript):
            # Handle generics like List[int], Dict[str, int]
            value = self._get_type_annotation_from_node(node.value)
            slice_val = self._get_type_annotation_from_node(node.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(node, ast.Tuple):
            # Handle multiple types like Union[int, str]
            types = [self._get_type_annotation_from_node(elt) for elt in node.elts]
            return ", ".join(types)
        else:
            return 'Any'
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            return self._get_name(decorator.func)
        return 'unknown'
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return 'unknown'
    
    def _get_default_value(self, node: ast.AST) -> Any:
        """Extract default value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.List):
            return []
        elif isinstance(node, ast.Dict):
            return {}
        return None
    
    def _find_exceptions(self, node: ast.FunctionDef) -> List[str]:
        """Find exceptions raised in function."""
        exceptions = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if child.exc:
                    exc_name = self._get_exception_name(child.exc)
                    if exc_name:
                        exceptions.append(exc_name)
        
        return list(set(exceptions))
    
    def _get_exception_name(self, node: ast.AST) -> Optional[str]:
        """Get exception name from raise statement."""
        if isinstance(node, ast.Call):
            return self._get_name(node.func)
        elif isinstance(node, ast.Name):
            return node.id
        return None
    
    def _has_assertions(self, node: ast.FunctionDef) -> bool:
        """Check if function contains assertions."""
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                return True
        return False
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity.
        
        Args:
            node: AST node
            
        Returns:
            Complexity score
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Each decision point adds to complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # And/Or operators
                complexity += len(child.values) - 1
        
        return complexity
