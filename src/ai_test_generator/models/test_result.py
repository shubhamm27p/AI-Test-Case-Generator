from typing import List, Optional
from pydantic import BaseModel, Field

class SingleTestResult(BaseModel):
    """Result of a single executed PyTest test."""
    test_id: str
    title: str
    status: str  # e.g., 'passed', 'failed', 'skipped', 'error'
    duration: float
    error_message: Optional[str] = None
    
class ExecutionResult(BaseModel):
    """Summary of the full PyTest execution."""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    pass_percentage: float = 0.0
    duration: float = 0.0
    coverage_percentage: Optional[float] = None
    tests: List[SingleTestResult] = Field(default_factory=list)
