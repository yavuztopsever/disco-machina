# DiscoMachina Tests

This directory contains tests for the DiscoMachina project.

## Test Structure

The tests are organized into the following directories:

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for API endpoints and component interactions
- `e2e/`: End-to-end tests for the terminal client and full flows

## Running Tests

You can run the tests using the provided script:

```bash
./run_tests.sh
```

Or manually with pytest:

```bash
# Run all tests
python -m pytest

# Run unit tests only
python -m pytest tests/unit

# Run integration tests only
python -m pytest tests/integration

# Run e2e tests only
python -m pytest tests/e2e

# Run tests with coverage
python -m pytest --cov=src tests/
```

## Test Dependencies

Test dependencies are listed in `requirements-dev.txt`. You can install them with:

```bash
pip install -r requirements-dev.txt
```

## Test Fixtures

Reusable test fixtures are defined in `conftest.py`. These include:

1. `temp_directory`: Creates a temporary directory for tests
2. `temp_file`: Creates a temporary file for tests
3. `mock_codebase`: Creates a mock codebase structure for testing

## Key Test Focus Areas

1. **Working Directory Flow**: Testing that the system properly uses the current directory as context
2. **CrewAI Integration**: Verifying proper handling of process types, memory, and delegation
3. **WebSocket Communication**: Testing real-time updates via WebSocket connections
4. **Error Recovery**: Verifying the exponential backoff retry mechanism
5. **Tool Selection**: Testing the ability to select and filter tools