# Project Structure

```
ai-test-generator/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD pipeline
├── docs/
│   └── getting-started.md            # Getting started guide
├── examples/
│   └── calculator.py                 # Example Python module for testing
├── src/
│   └── ai_test_generator/
│       ├── __init__.py               # Package initialization
│       ├── analyzer.py               # Code analysis using AST
│       ├── cli.py                    # Command-line interface
│       ├── config.py                 # Configuration management
│       ├── edge_case_detector.py     # Edge case detection logic
│       ├── generator.py              # Main test generator class
│       ├── ml_model.py               # Machine learning model
│       ├── templates.py              # Test code templates
│       └── user_story_parser.py      # User story parsing
├── tests/
│   └── test_generator.py             # Unit tests
├── .ai-test-gen.example.yml          # Example configuration
├── .gitignore                        # Git ignore rules
├── CHANGELOG.md                      # Version history
├── CONTRIBUTING.md                   # Contribution guidelines
├── LICENSE                           # MIT License
├── Makefile                          # Common development tasks
├── README.md                         # Main documentation
├── demo.py                           # Demo/quickstart script
├── pyproject.toml                    # Modern Python packaging
├── pytest.ini                        # Pytest configuration
├── requirements-dev.txt              # Development dependencies
├── requirements.txt                  # Production dependencies
└── setup.py                          # Package setup
```

## Directory Descriptions

### Root Directory
- **README.md**: Main project documentation with features, installation, and usage
- **LICENSE**: MIT License
- **CHANGELOG.md**: Version history and release notes
- **CONTRIBUTING.md**: Guidelines for contributors
- **setup.py**: Package installation configuration
- **pyproject.toml**: Modern Python packaging configuration
- **pytest.ini**: Pytest configuration
- **Makefile**: Convenient commands for development tasks
- **demo.py**: Interactive demo script
- **.gitignore**: Git ignore patterns
- **.ai-test-gen.example.yml**: Example configuration file

### src/ai_test_generator/
Core package containing all source code:

- **__init__.py**: Package exports and version
- **generator.py**: Main `TestGenerator` class that orchestrates test generation
- **analyzer.py**: `CodeAnalyzer` class for parsing Python code using AST
- **edge_case_detector.py**: `EdgeCaseDetector` for identifying edge cases
- **ml_model.py**: Machine learning model for test prediction
- **templates.py**: Test code generation templates for pytest/unittest
- **user_story_parser.py**: Parser for user stories and BDD scenarios
- **cli.py**: Command-line interface implementation
- **config.py**: Configuration file handling and defaults

### tests/
Test suite for the project:

- **test_generator.py**: Comprehensive unit tests for all components
- Additional test files can be added as the project grows

### docs/
Documentation files:

- **getting-started.md**: Step-by-step guide for new users
- Additional documentation can be added (API docs, tutorials, etc.)

### examples/
Example code and demonstrations:

- **calculator.py**: Sample Python module to demonstrate test generation
- Generated tests will be placed in `examples/generated_tests/`

### .github/workflows/
CI/CD configuration:

- **ci.yml**: GitHub Actions workflow for automated testing and building

## Key Files

### Configuration
- `.ai-test-gen.example.yml`: Template configuration file
- Users copy this to `.ai-test-gen.yml` and customize

### Requirements
- `requirements.txt`: Production dependencies (numpy, tensorflow, pytest, etc.)
- `requirements-dev.txt`: Development tools (black, flake8, mypy, etc.)

### Testing
- `pytest.ini`: Pytest settings including coverage configuration
- `tests/`: All unit and integration tests

### Packaging
- `setup.py`: Traditional setuptools configuration
- `pyproject.toml`: Modern PEP 517/518 packaging
- Both files ensure compatibility with different Python packaging tools

## Development Workflow

1. **Install**: `make install-dev`
2. **Run Tests**: `make test`
3. **Format Code**: `make format`
4. **Run Linters**: `make lint`
5. **Check Coverage**: `make coverage`
6. **Run Demo**: `make demo`
7. **Build Package**: `make build`

## Module Dependencies

```
generator.py
├── analyzer.py (code analysis)
├── edge_case_detector.py (edge cases)
├── ml_model.py (AI predictions)
├── templates.py (code generation)
└── user_story_parser.py (story parsing)

cli.py
├── generator.py (main logic)
└── config.py (configuration)

All modules
└── config.py (shared configuration)
```

## Entry Points

1. **CLI**: `ai-test-gen` command (defined in setup.py)
2. **Python API**: Import `from ai_test_generator import TestGenerator`
3. **Demo**: `python demo.py`

## Output Structure

When generating tests, the default structure is:

```
your-project/
├── src/
│   └── module.py
└── tests/
    └── test_module.py  # Generated tests
```

Customizable via configuration.
