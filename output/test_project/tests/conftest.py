"""
Shared fixtures for all tests.
"""

import pytest
from calculator import Calculator

@pytest.fixture
def calculator():
    """Return a fresh Calculator instance for each test."""
    return Calculator()

@pytest.fixture
def calculator_with_initial_value():
    """Return a Calculator instance with initial value set to 10."""
    calc = Calculator()
    calc.add(10)
    return calc