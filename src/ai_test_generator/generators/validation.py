import logging
from typing import List
from ..models.test_case import TestCase
from ..exceptions import ValidationError

logger = logging.getLogger(__name__)

class TestCaseValidator:
    """
    Validation Layer: Ensures AI-generated test cases meet strict quality standards
    before they are passed to the code generation phase.
    """
    
    @staticmethod
    def validate(test_cases: List[TestCase]) -> List[TestCase]:
        if not test_cases:
            raise ValidationError("Empty test case list provided for validation.")
            
        seen_ids = set()
        seen_titles = set()
        validated_cases = []
        
        for tc in test_cases:
            # Check required fields
            if not tc.title or not tc.expected_result:
                logger.warning(f"Dropping test case {tc.test_case_id}: Missing title or expected result.")
                continue
                
            # Duplicate ID check
            if tc.test_case_id in seen_ids:
                logger.warning(f"Dropping test case {tc.title}: Duplicate ID {tc.test_case_id}.")
                continue
                
            # Duplicate scenario check
            title_lower = tc.title.lower().strip()
            if title_lower in seen_titles:
                logger.warning(f"Dropping test case {tc.test_case_id}: Duplicate scenario '{tc.title}'.")
                continue
                
            # Validation passed
            seen_ids.add(tc.test_case_id)
            seen_titles.add(title_lower)
            validated_cases.append(tc)
            
        if not validated_cases:
            raise ValidationError("All generated test cases failed validation checks.")
            
        return validated_cases
