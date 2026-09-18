"""
Custom Exceptions for AI Test Generator
"""

class AITestGeneratorError(Exception):
    """Base exception for all AI Test Generator errors."""
    pass

class ConfigurationError(AITestGeneratorError):
    """Raised when there is a configuration issue."""
    pass

class LLMError(AITestGeneratorError):
    """Raised when the LLM API fails."""
    pass

class GenerationError(AITestGeneratorError):
    """Raised when generation fails."""
    pass

class ValidationError(AITestGeneratorError):
    """Raised when validation of output fails."""
    pass

class TestExecutionError(AITestGeneratorError):
    """Raised when execution of tests fails."""
    pass

class ReportGenerationError(AITestGeneratorError):
    """Raised when report generation fails."""
    pass
