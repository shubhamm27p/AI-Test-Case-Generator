# Contributing to AI Test Generator

Thank you for your interest in contributing to AI Test Generator! We welcome contributions from the community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/ai-test-generator.git
   cd ai-test-generator
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use prefixes:
- `feature/` for new features
- `bugfix/` for bug fixes
- `docs/` for documentation
- `refactor/` for code refactoring

### 2. Make Your Changes

- Write clear, concise code
- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Include type hints where appropriate

### 3. Write Tests

- Add tests for new functionality
- Ensure all tests pass:
  ```bash
  pytest tests/
  ```
- Check code coverage:
  ```bash
  pytest --cov=ai_test_generator --cov-report=html
  ```

### 4. Code Quality

Run these tools before committing:

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# Sort imports
isort src/ tests/
```

### 5. Commit Your Changes

Write clear commit messages:

```bash
git add .
git commit -m "Add feature: brief description"
```

Follow the conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for refactoring

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings (Google style)

### Example:

```python
def calculate_complexity(node: ast.AST) -> int:
    """
    Calculate cyclomatic complexity of code.
    
    Args:
        node: AST node to analyze
        
    Returns:
        Complexity score
        
    Raises:
        ValueError: If node is invalid
    """
    pass
```

## Testing Guidelines

- Write unit tests for all new functions
- Use pytest fixtures for common setup
- Mock external dependencies
- Aim for >80% code coverage
- Test edge cases and error conditions

### Example Test:

```python
def test_edge_case_detector():
    """Test edge case detection for integers."""
    detector = EdgeCaseDetector()
    func_info = {
        'name': 'test_func',
        'parameters': [{'name': 'x', 'type': 'int'}]
    }
    
    tests = detector.detect_edge_cases(func_info)
    
    assert len(tests) > 0
    assert any(t['params']['x'] == 0 for t in tests)
```

## Documentation

- Update README.md if adding features
- Add docstrings to all public functions
- Update CHANGELOG.md
- Add examples for new features

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass** locally
4. **Update CHANGELOG.md** with your changes
5. **Create pull request** with clear description
6. **Address review comments** promptly

### Pull Request Template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Updated documentation

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
```

## Reporting Bugs

Use GitHub Issues and include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Exact steps to reproduce
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: Python version, OS, etc.
- **Code Sample**: Minimal code to reproduce

## Feature Requests

Submit feature requests via GitHub Issues:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Additional Context**: Any other relevant info

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on what's best for the community
- Show empathy towards others

## Questions?

- Open a GitHub Discussion
- Check existing issues
- Read the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be acknowledged in:
- README.md
- CHANGELOG.md
- GitHub releases

Thank you for contributing! 🎉
