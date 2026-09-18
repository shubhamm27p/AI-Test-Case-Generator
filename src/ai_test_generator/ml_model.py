"""
Machine Learning Model Module
Uses neural networks to predict test cases based on patterns.
"""

import os
import json
import numpy as np
from typing import Dict, List, Any, Optional

TENSORFLOW_AVAILABLE = None
tf = None
keras = None

def _check_tensorflow():
    global TENSORFLOW_AVAILABLE, tf, keras
    if TENSORFLOW_AVAILABLE is not None:
        return TENSORFLOW_AVAILABLE
    try:
        import tensorflow as _tf
        from tensorflow import keras as _keras
        tf = _tf
        keras = _keras
        TENSORFLOW_AVAILABLE = True
    except ImportError:
        TENSORFLOW_AVAILABLE = False
    return TENSORFLOW_AVAILABLE

class TestCaseModel:
    """
    ML model for predicting test cases based on code patterns.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the ML model.
        
        Args:
            model_path: Path to pre-trained model file
        """
        self.model = None
        self.model_path = model_path
        self.vectorizer = CodeVectorizer()
        
        if _check_tensorflow() and model_path and os.path.exists(model_path):
            self.load_model(model_path)
        elif _check_tensorflow():
            self.model = self._build_model()
    
    def _build_model(self) -> Optional['keras.Model']:
        """
        Build the neural network model architecture.
        
        Returns:
            Keras model
        """
        if not _check_tensorflow():
            return None
        
        # Input layer - function signature features
        inputs = keras.Input(shape=(100,), name='function_features')
        
        # LSTM for sequence processing
        x = keras.layers.Reshape((10, 10))(inputs)
        x = keras.layers.LSTM(64, return_sequences=True)(x)
        x = keras.layers.LSTM(32)(x)
        
        # Dense layers for classification
        x = keras.layers.Dense(64, activation='relu')(x)
        x = keras.layers.Dropout(0.3)(x)
        x = keras.layers.Dense(32, activation='relu')(x)
        
        # Output layers for different test types
        output_test_type = keras.layers.Dense(10, activation='softmax', name='test_type')(x)
        output_complexity = keras.layers.Dense(1, activation='linear', name='complexity')(x)
        
        model = keras.Model(inputs=inputs, outputs=[output_test_type, output_complexity])
        
        model.compile(
            optimizer='adam',
            loss={
                'test_type': 'categorical_crossentropy',
                'complexity': 'mse'
            },
            metrics={
                'test_type': 'accuracy',
                'complexity': 'mae'
            }
        )
        
        return model
    
    def predict_test_cases(
        self,
        func_info: Dict[str, Any],
        max_suggestions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Predict test cases using the ML model.
        
        Args:
            func_info: Function information from analyzer
            max_suggestions: Maximum number of test suggestions
            
        Returns:
            List of predicted test cases
        """
        # If model not available, return heuristic-based suggestions
        if not _check_tensorflow() or self.model is None:
            return self._heuristic_suggestions(func_info, max_suggestions)
        
        # Vectorize function information
        features = self.vectorizer.vectorize(func_info)
        features = np.array([features])
        
        # Predict
        test_types, complexity = self.model.predict(features, verbose=0)
        
        # Convert predictions to test cases
        test_cases = self._predictions_to_test_cases(
            func_info,
            test_types[0],
            complexity[0][0],
            max_suggestions
        )
        
        return test_cases
    
    def _heuristic_suggestions(
        self,
        func_info: Dict[str, Any],
        max_suggestions: int
    ) -> List[Dict[str, Any]]:
        """
        Generate test suggestions using heuristics when ML is unavailable.
        
        Args:
            func_info: Function information
            max_suggestions: Maximum suggestions
            
        Returns:
            List of suggested test cases
        """
        suggestions = []
        
        # Suggestion 1: Test with typical values
        suggestions.append({
            'type': 'ml_suggested',
            'function': func_info['name'],
            'description': f"ML suggested: Test {func_info['name']} with typical values",
            'params': self._generate_typical_params(func_info),
            'expected': 'success',
            'confidence': 0.8
        })
        
        # Suggestion 2: Test with boundary values
        if func_info.get('complexity', 0) > 5:
            suggestions.append({
                'type': 'ml_suggested',
                'function': func_info['name'],
                'description': f"ML suggested: Test complex function {func_info['name']} with edge cases",
                'params': self._generate_boundary_params(func_info),
                'expected': 'edge_case',
                'confidence': 0.7
            })
        
        # Suggestion 3: Test exception paths
        if func_info.get('raises'):
            suggestions.append({
                'type': 'ml_suggested',
                'function': func_info['name'],
                'description': f"ML suggested: Test exception handling in {func_info['name']}",
                'params': self._generate_exception_params(func_info),
                'expected': 'exception',
                'confidence': 0.75
            })
        
        return suggestions[:max_suggestions]
    
    def _generate_typical_params(self, func_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate typical parameter values."""
        params = {}
        
        for param in func_info.get('parameters', []):
            param_type = param.get('type', 'Any')
            
            if param_type == 'int':
                params[param['name']] = 42
            elif param_type == 'float':
                params[param['name']] = 3.14
            elif param_type == 'str':
                params[param['name']] = "sample"
            elif param_type == 'bool':
                params[param['name']] = True
            elif param_type == 'list':
                params[param['name']] = [1, 2, 3]
            elif param_type == 'dict':
                params[param['name']] = {"key": "value"}
        
        return params
    
    def _generate_boundary_params(self, func_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate boundary parameter values."""
        params = {}
        
        for param in func_info.get('parameters', []):
            param_type = param.get('type', 'Any')
            
            if param_type == 'int':
                params[param['name']] = 0
            elif param_type == 'float':
                params[param['name']] = 0.0
            elif param_type == 'str':
                params[param['name']] = ""
            elif param_type == 'list':
                params[param['name']] = []
            elif param_type == 'dict':
                params[param['name']] = {}
        
        return params
    
    def _generate_exception_params(self, func_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate parameters that should trigger exceptions."""
        params = {}
        
        for param in func_info.get('parameters', []):
            params[param['name']] = None
        
        return params
    
    def _predictions_to_test_cases(
        self,
        func_info: Dict[str, Any],
        test_type_probs: np.ndarray,
        complexity: float,
        max_suggestions: int
    ) -> List[Dict[str, Any]]:
        """Convert model predictions to test case specifications."""
        test_types = [
            'happy_path', 'boundary', 'null_check', 'exception',
            'integration', 'performance', 'security', 'concurrency',
            'data_validation', 'error_recovery'
        ]
        
        # Get top predictions
        top_indices = np.argsort(test_type_probs)[-max_suggestions:][::-1]
        
        test_cases = []
        for idx in top_indices:
            test_type = test_types[idx]
            confidence = float(test_type_probs[idx])
            
            if confidence > 0.5:  # Only include confident predictions
                test_cases.append({
                    'type': 'ml_predicted',
                    'function': func_info['name'],
                    'description': f"ML predicted: {test_type} test for {func_info['name']}",
                    'test_type': test_type,
                    'confidence': confidence,
                    'complexity': float(complexity)
                })
        
        return test_cases
    
    def train(
        self,
        training_data: List[Dict[str, Any]],
        epochs: int = 50,
        validation_split: float = 0.2
    ):
        """
        Train the model on historical test case data.
        
        Args:
            training_data: List of training examples
            epochs: Number of training epochs
            validation_split: Validation data split ratio
        """
        if not _check_tensorflow() or self.model is None:
            raise RuntimeError("TensorFlow not available or model not initialized")
        
        # Prepare training data
        X = []
        y_type = []
        y_complexity = []
        
        for example in training_data:
            features = self.vectorizer.vectorize(example['function'])
            X.append(features)
            y_type.append(example['test_type_encoded'])
            y_complexity.append(example['complexity'])
        
        X = np.array(X)
        y_type = np.array(y_type)
        y_complexity = np.array(y_complexity)
        
        # Train model
        history = self.model.fit(
            X,
            {'test_type': y_type, 'complexity': y_complexity},
            epochs=epochs,
            validation_split=validation_split,
            verbose=1
        )
        
        return history
    
    def save_model(self, path: str):
        """Save the trained model."""
        if _check_tensorflow() and self.model:
            self.model.save(path)
    
    def load_model(self, path: str):
        """Load a pre-trained model."""
        if _check_tensorflow():
            self.model = keras.models.load_model(path)


class CodeVectorizer:
    """
    Converts code features into numerical vectors for ML model.
    """
    
    def vectorize(self, func_info: Dict[str, Any]) -> np.ndarray:
        """
        Convert function information to feature vector.
        
        Args:
            func_info: Function information dictionary
            
        Returns:
            Feature vector (100 dimensions)
        """
        features = np.zeros(100)
        
        # Features 0-9: Number of parameters
        num_params = len(func_info.get('parameters', []))
        features[0] = min(num_params, 10) / 10.0
        
        # Features 10-19: Parameter type distribution
        param_types = [p.get('type', 'Any') for p in func_info.get('parameters', [])]
        type_counts = {
            'int': param_types.count('int'),
            'float': param_types.count('float'),
            'str': param_types.count('str'),
            'bool': param_types.count('bool'),
            'list': sum(1 for t in param_types if 'list' in t.lower()),
            'dict': sum(1 for t in param_types if 'dict' in t.lower()),
        }
        
        for i, (_, count) in enumerate(type_counts.items()):
            if i < 10:
                features[10 + i] = count / max(num_params, 1)
        
        # Features 20-29: Function complexity
        complexity = func_info.get('complexity', 1)
        features[20] = min(complexity, 10) / 10.0
        
        # Features 30-39: Exception handling
        num_exceptions = len(func_info.get('raises', []))
        features[30] = min(num_exceptions, 10) / 10.0
        
        # Features 40-49: Return type
        return_type = func_info.get('return_type', 'None')
        if return_type == 'int':
            features[40] = 1.0
        elif return_type == 'str':
            features[41] = 1.0
        elif return_type == 'bool':
            features[42] = 1.0
        elif 'list' in return_type.lower():
            features[43] = 1.0
        elif 'dict' in return_type.lower():
            features[44] = 1.0
        
        # Features 50-59: Decorators
        decorators = func_info.get('decorators', [])
        if 'property' in decorators:
            features[50] = 1.0
        if 'staticmethod' in decorators:
            features[51] = 1.0
        if 'classmethod' in decorators:
            features[52] = 1.0
        
        # Features 60-99: Reserved for future use
        
        return features
