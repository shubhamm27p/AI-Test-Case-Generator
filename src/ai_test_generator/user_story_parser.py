"""
User Story Parser Module
Parses user stories and converts them to test scenarios.
"""

import re
from typing import Dict, List, Any


class UserStoryParser:
    """
    Parses user stories using NLP techniques and generates test scenarios.
    """
    
    def __init__(self):
        self.story_pattern = re.compile(
            r'^\s*As\s+(?:a|an)\s+(.+?),?\s+I\s+want\s+(?:to\s+)?(.+?)(?:,?\s+so\s+that\s+(.+?))?\s*$',
            re.IGNORECASE
        )
        
        self.acceptance_pattern = re.compile(
            r'Given\s+(.+?)\s+When\s+(.+?)\s+Then\s+(.+)',
            re.IGNORECASE | re.DOTALL
        )
    
    def parse(self, user_story: str) -> Dict[str, Any]:
        """
        Parse a user story into structured format.
        
        Args:
            user_story: User story text
            
        Returns:
            Parsed story structure
        """
        story_data = {
            'raw': user_story,
            'role': None,
            'action': None,
            'benefit': None,
            'acceptance_criteria': []
        }
        
        # Try to match standard user story format
        match = self.story_pattern.search(user_story)
        if match:
            story_data['role'] = match.group(1).strip()
            story_data['action'] = match.group(2).strip()
            story_data['benefit'] = match.group(3).strip() if match.group(3) else None
        else:
            # Fallback: treat entire text as action
            story_data['action'] = user_story.strip()
        
        # Extract acceptance criteria (Given-When-Then format)
        acceptance_matches = self.acceptance_pattern.finditer(user_story)
        for match in acceptance_matches:
            story_data['acceptance_criteria'].append({
                'given': match.group(1).strip(),
                'when': match.group(2).strip(),
                'then': match.group(3).strip()
            })
        
        return story_data
    
    def generate_test_scenarios(
        self,
        parsed_story: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate test scenarios from parsed user story.
        
        Args:
            parsed_story: Parsed story structure
            
        Returns:
            List of test scenarios
        """
        scenarios = []
        
        # If acceptance criteria exist, use them
        if parsed_story['acceptance_criteria']:
            for i, criteria in enumerate(parsed_story['acceptance_criteria']):
                scenarios.append({
                    'title': f"Acceptance Criteria {i+1}",
                    'given': criteria['given'],
                    'when': criteria['when'],
                    'then': criteria['then'],
                    'type': 'acceptance'
                })
        else:
            # Generate scenarios from story components
            scenarios.extend(self._generate_default_scenarios(parsed_story))
        
        return scenarios
    
    def _generate_default_scenarios(
        self,
        parsed_story: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate default test scenarios from story."""
        scenarios = []
        action = parsed_story.get('action', '')
        role = parsed_story.get('role', 'user')
        
        # Happy path scenario
        scenarios.append({
            'title': 'Happy Path',
            'given': f'the {role} is authenticated',
            'when': f'the {role} performs: {action}',
            'then': 'the action completes successfully',
            'type': 'happy_path'
        })
        
        # Error scenario
        scenarios.append({
            'title': 'Error Handling',
            'given': f'the {role} provides invalid input',
            'when': f'the {role} attempts: {action}',
            'then': 'an appropriate error message is displayed',
            'type': 'error_handling'
        })
        
        # Edge case scenario
        scenarios.append({
            'title': 'Edge Case',
            'given': f'the {role} has minimal permissions',
            'when': f'the {role} tries: {action}',
            'then': 'the system handles the edge case appropriately',
            'type': 'edge_case'
        })
        
        return scenarios
    
    def extract_test_data(self, parsed_story: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract test data suggestions from story.
        
        Args:
            parsed_story: Parsed story structure
            
        Returns:
            Test data suggestions
        """
        test_data = {
            'valid_inputs': [],
            'invalid_inputs': [],
            'edge_cases': []
        }
        
        action = parsed_story.get('action', '').lower()
        
        # Extract entities and actions
        if 'login' in action:
            test_data['valid_inputs'].append({
                'email': 'user@example.com',
                'password': 'ValidPassword123!'
            })
            test_data['invalid_inputs'].append({
                'email': 'invalid-email',
                'password': '123'
            })
            test_data['edge_cases'].append({
                'email': '',
                'password': ''
            })
        
        elif 'create' in action or 'add' in action:
            test_data['valid_inputs'].append({
                'name': 'Test Item',
                'description': 'A valid test item'
            })
            test_data['invalid_inputs'].append({
                'name': '',
                'description': None
            })
        
        elif 'search' in action or 'find' in action:
            test_data['valid_inputs'].append({
                'query': 'valid search term'
            })
            test_data['invalid_inputs'].append({
                'query': ''
            })
            test_data['edge_cases'].append({
                'query': 'x' * 1000  # Very long query
            })
        
        elif 'delete' in action or 'remove' in action:
            test_data['valid_inputs'].append({
                'id': 123
            })
            test_data['invalid_inputs'].append({
                'id': -1
            })
            test_data['edge_cases'].append({
                'id': None
            })
        
        return test_data
    
    def identify_test_types(self, parsed_story: Dict[str, Any]) -> List[str]:
        """
        Identify which types of tests are needed.
        
        Args:
            parsed_story: Parsed story structure
            
        Returns:
            List of test types
        """
        test_types = ['functional']  # Always include functional tests
        
        action = parsed_story.get('action', '').lower()
        benefit = parsed_story.get('benefit', '').lower() if parsed_story.get('benefit') else ''
        
        # Security tests
        if any(word in action for word in ['login', 'authenticate', 'authorize', 'permission']):
            test_types.append('security')
        
        # Performance tests
        if any(word in benefit for word in ['fast', 'quickly', 'performance', 'speed']):
            test_types.append('performance')
        
        # Integration tests
        if any(word in action for word in ['integrate', 'connect', 'sync', 'api']):
            test_types.append('integration')
        
        # UI tests
        if any(word in action for word in ['click', 'view', 'display', 'show', 'interface']):
            test_types.append('ui')
        
        # Data validation tests
        if any(word in action for word in ['validate', 'verify', 'check', 'ensure']):
            test_types.append('validation')
        
        return test_types
    
    def generate_bdd_scenarios(
        self,
        parsed_story: Dict[str, Any]
    ) -> str:
        """
        Generate BDD (Behavior-Driven Development) scenarios in Gherkin format.
        
        Args:
            parsed_story: Parsed story structure
            
        Returns:
            Gherkin feature file content
        """
        action = parsed_story.get('action', 'perform action')
        role = parsed_story.get('role', 'user')
        benefit = parsed_story.get('benefit', 'achieve goal')
        
        gherkin = f'''Feature: {action.title()}
  As a {role}
  I want to {action}
  So that {benefit}

'''
        
        scenarios = self.generate_test_scenarios(parsed_story)
        
        for scenario in scenarios:
            gherkin += f'''  Scenario: {scenario['title']}
    Given {scenario['given']}
    When {scenario['when']}
    Then {scenario['then']}

'''
        
        return gherkin
