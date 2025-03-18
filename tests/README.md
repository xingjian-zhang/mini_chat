# Mini-Chat Tests

This directory contains tests for the Mini-Chat application using pytest.

## Running Tests

There are multiple ways to run the tests:

1. Using the provided script:
```bash
./scripts/run_tests.sh
```

2. Using pytest directly:
```bash
python -m pytest
```

3. With coverage reports:
```bash
python -m pytest --cov=mini_chat --cov-report=term --cov-report=html
```

## Test Organization

The tests are organized by module to mirror the application structure:

- `test_models.py`: Tests for data models
- `test_config.py`: Tests for configuration management
- `test_api.py`: Tests for API communication
- `test_ui.py`: Tests for UI components
- `test_main.py`: Tests for the main application

## Test Fixtures

Common test fixtures are defined in `conftest.py` and are available to all test modules.

## Writing New Tests

When adding new features to the application, please ensure you also add tests for those features. Follow these guidelines:

1. Create test functions with clear names describing what they test
2. Use descriptive docstrings for each test function
3. Use fixtures when appropriate to reduce code duplication
4. Mock external dependencies to ensure tests run quickly and reliably
5. Test both success and failure cases

## Coverage

The tests aim to maintain high code coverage. Coverage reports are generated automatically when running tests with coverage enabled.
