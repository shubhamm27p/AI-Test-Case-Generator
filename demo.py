#!/usr/bin/env python
"""
Quickstart Demo for AI Test Generator

This script demonstrates the basic usage of the AI Test Generator.
"""

import sys
from pathlib import Path

# Add src to path for demo
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ai_test_generator import TestGenerator


def demo_basic_usage():
    """Demonstrate basic usage."""
    print("=" * 60)
    print("AI Test Generator - Quickstart Demo")
    print("=" * 60)
    print()
    
    # Initialize generator
    print("1. Initializing Test Generator...")
    generator = TestGenerator()
    print("   ✓ Generator initialized")
    print()
    
    # Analyze example file
    example_file = Path(__file__).parent / 'examples' / 'calculator.py'
    
    if not example_file.exists():
        print(f"   ✗ Example file not found: {example_file}")
        return
    
    print(f"2. Analyzing example file: {example_file.name}")
    test_cases = generator.analyze_file(str(example_file))
    print(f"   ✓ Generated {len(test_cases)} test case specifications")
    print()
    
    # Show some test cases
    print("3. Sample test cases:")
    for i, test_case in enumerate(test_cases[:5], 1):
        print(f"   {i}. {test_case.get('description', 'No description')}")
    if len(test_cases) > 5:
        print(f"   ... and {len(test_cases) - 5} more")
    print()
    
    # Generate test file
    print("4. Generating test file...")
    output_dir = Path(__file__).parent / 'examples' / 'generated_tests'
    output_dir.mkdir(exist_ok=True)
    
    output_path = generator.generate_test_file(
        str(example_file),
        output_path=str(output_dir / 'test_calculator.py'),
        include_edge_cases=True
    )
    print(f"   ✓ Test file generated: {output_path}")
    print()
    
    # Show snippet of generated code
    print("5. Preview of generated test code:")
    print("   " + "-" * 56)
    with open(output_path, 'r') as f:
        lines = f.readlines()[:20]
        for line in lines:
            print(f"   {line.rstrip()}")
    print("   " + "-" * 56)
    print()


def demo_user_story():
    """Demonstrate user story parsing."""
    print("=" * 60)
    print("User Story Test Generation Demo")
    print("=" * 60)
    print()
    
    generator = TestGenerator()
    
    # Example user story
    user_story = """
    As a user,
    I want to login with my email and password,
    so that I can access my account securely
    """
    
    print("User Story:")
    print(user_story)
    print()
    
    print("Generating test scenarios...")
    output_dir = Path(__file__).parent / 'examples' / 'generated_tests'
    output_dir.mkdir(exist_ok=True)
    
    output_path = generator.generate_from_user_story(
        user_story,
        output_path=str(output_dir / 'test_user_story.py')
    )
    
    print(f"✓ Test file generated: {output_path}")
    print()
    
    # Show preview
    print("Preview:")
    print("-" * 60)
    with open(output_path, 'r') as f:
        print(f.read())
    print("-" * 60)


def main():
    """Run demos."""
    try:
        demo_basic_usage()
        print()
        demo_user_story()
        
        print()
        print("=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Explore the generated test files in examples/generated_tests/")
        print("  2. Try: ai-test-gen analyze examples/calculator.py")
        print("  3. Read the documentation in README.md")
        print()
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
