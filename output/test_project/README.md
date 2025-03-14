# Calculator Test Project

A simple calculator application with a comprehensive test suite demonstrating different testing approaches.

## Features

- Basic arithmetic operations (add, subtract, multiply, divide)
- Command-line interface
- Comprehensive test suite (unit, integration, E2E, UAT)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/calculator-test-project.git
cd calculator-test-project

# Install the package in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## Usage

```bash
# Using the CLI
calculator add 5 3
calculator subtract 10 4
calculator multiply 6 7
calculator divide 20 5

# Or from Python code
from calculator import Calculator, add_numbers

# Using standalone function
result = add_numbers(5, 3)
print(result)  # 8

# Using Calculator class
calc = Calculator()
calc.add(10)       # result = 10
calc.subtract(4)   # result = 6
calc.multiply(3)   # result = 18
calc.divide(2)     # result = 9
```

## Testing

This project demonstrates multiple testing approaches:

### Unit Tests

Test individual functions and classes in isolation.

```bash
python -m pytest tests/unit -v
```

### Integration Tests

Test interactions between different components.

```bash
python -m pytest tests/integration -v
```

### End-to-End (E2E) Tests

Test the complete application workflow.

```bash
python -m pytest tests/e2e -v
```

### User Acceptance Tests (UAT)

Behavior-driven tests verifying user requirements.

```bash
behave tests/uat/features
```

### Run All Tests

Use the provided script to run all tests:

```bash
./run_tests.sh
```

## Test Environment Setup

Using conda/mamba:

```bash
# Create environment from environment.yml
conda env create -f environment.yml
# Activate environment
conda activate calculator-test-env
```

Manual setup:

```bash
# Install required packages
pip install pytest pytest-cov pytest-mock pytest-xdist behave
pip install flake8 black mypy
```

## Project Structure

```
calculator-test-project/
├── calculator/           # Main package
│   ├── __init__.py
│   ├── calculator.py     # Core functionality
│   └── cli.py            # Command-line interface
├── tests/                # Test suite
│   ├── conftest.py       # Shared test fixtures
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── e2e/              # End-to-end tests
│   └── uat/              # User acceptance tests
│       └── features/     # BDD feature specifications
├── environment.yml       # Conda environment definition
├── pytest.ini           # Pytest configuration
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
├── run.py               # Script to run the calculator
├── run_tests.sh         # Script to run all tests
└── setup.py             # Package installation
```

## License

MIT