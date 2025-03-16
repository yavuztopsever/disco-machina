"""
Configuration file for pytest.
Contains fixtures and setup/teardown functions for tests.
"""

import os
import sys
import pytest
import tempfile
import shutil

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_file():
    """Create a temporary file for tests."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"Test content")
        file_path = f.name
    yield file_path
    # Cleanup
    if os.path.exists(file_path):
        os.unlink(file_path)


@pytest.fixture
def mock_codebase(temp_directory):
    """Create a mock codebase for testing."""
    # Create some directories
    os.makedirs(os.path.join(temp_directory, "src"), exist_ok=True)
    os.makedirs(os.path.join(temp_directory, "tests"), exist_ok=True)
    os.makedirs(os.path.join(temp_directory, "docs"), exist_ok=True)
    
    # Create some files
    with open(os.path.join(temp_directory, "README.md"), "w") as f:
        f.write("# Test Project\n\nThis is a test project for testing.")
    
    with open(os.path.join(temp_directory, "src", "main.py"), "w") as f:
        f.write('def main():\n    print("Hello, world!")\n\nif __name__ == "__main__":\n    main()')
    
    with open(os.path.join(temp_directory, "tests", "test_main.py"), "w") as f:
        f.write('import unittest\n\nclass TestMain(unittest.TestCase):\n    def test_main(self):\n        self.assertTrue(True)')
    
    yield temp_directory