#!/usr/bin/env python3
"""
Simplified end-to-end tests for the terminal client.
These tests verify basic functionality without mocking sys.argv.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
import json
import subprocess
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class TestTerminalClient(unittest.TestCase):
    """Test case for the terminal client"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        # Change to the temp directory
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create a test file in the temp directory
        with open("test_file.txt", "w") as f:
            f.write("Test content")

    def tearDown(self):
        """Tear down test fixtures"""
        # Change back to the original directory
        os.chdir(self.original_dir)
        # Remove the temp directory
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch("requests.post")
    def test_workspace_context_generation(self, mock_post):
        """Test the workspace context generation functionality"""
        # This test verifies that get_workspace_info correctly identifies
        # the current directory structure
        
        # Import get_workspace_info directly
        from terminal_client import get_workspace_info
        
        # Create additional files and directories for testing
        os.makedirs(os.path.join(self.temp_dir, "src"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "tests"), exist_ok=True)
        
        # Create a package.json file 
        with open("package.json", "w") as f:
            f.write('{"name": "test-package"}')
            
        # Create a README.md file
        with open("README.md", "w") as f:
            f.write("# Test Project")
        
        # Get workspace info
        workspace_info = get_workspace_info()
        
        # Verify workspace info contains correct details
        # Use os.path.samefile to handle macOS /private path differences
        self.assertEqual(os.path.basename(workspace_info["path"]), os.path.basename(self.temp_dir))
        self.assertEqual(workspace_info["name"], os.path.basename(self.temp_dir))
        self.assertIn("test_file.txt", workspace_info["files"])
        self.assertIn("package.json", workspace_info["config_files"])
        self.assertIn("README.md", workspace_info["config_files"])
        self.assertIn("src", workspace_info["directories"])
        self.assertIn("tests", workspace_info["directories"])

    def test_current_directory_resolution(self):
        """Test that resolve_workspace_path correctly uses current directory"""
        # Import resolve_workspace_path directly
        from terminal_client import resolve_workspace_path
        
        # Call without argument
        workspace_path = resolve_workspace_path()
        
        # Verify it returns the current directory (using basename to handle macOS /private paths)
        self.assertEqual(os.path.basename(workspace_path), os.path.basename(self.temp_dir))
        
        # Call with argument
        test_path = os.path.join(self.temp_dir, "src")
        os.makedirs(test_path, exist_ok=True)
        workspace_path = resolve_workspace_path(test_path)
        
        # Verify it returns the specified directory (using basename)
        self.assertEqual(os.path.basename(workspace_path), os.path.basename(test_path))
        
        # Verify it handles relative paths correctly
        rel_path = "src"
        workspace_path = resolve_workspace_path(rel_path)
        self.assertEqual(os.path.basename(workspace_path), os.path.basename(os.path.join(self.temp_dir, rel_path)))

    def test_chat_history_initialization(self):
        """Test that initialize_chat_history creates proper context"""
        # Import initialize_chat_history directly
        from terminal_client import initialize_chat_history
        
        # Call with current directory
        chat_history = initialize_chat_history(self.temp_dir)
        
        # Verify it creates a proper system message
        self.assertEqual(len(chat_history), 1)
        self.assertEqual(chat_history[0]["role"], "system")
        
        # Verify the system message contains workspace context
        system_message = chat_history[0]["content"]
        self.assertIn(self.temp_dir, system_message)
        self.assertIn(os.path.basename(self.temp_dir), system_message)
        self.assertIn("test_file.txt", system_message)

    @patch("terminal_client.requests.get")
    def test_server_status_check(self, mock_get):
        """Test server status checking functionality"""
        # Import check_server_status directly
        from terminal_client import check_server_status
        
        # Test when server is available
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Check server status
        status = check_server_status("http://localhost:8000")
        
        # Verify it returns True for 200 response
        self.assertTrue(status)
        mock_get.assert_called_once_with("http://localhost:8000/health")
        
        # Test when server is unavailable
        mock_get.reset_mock()
        mock_get.side_effect = Exception("Connection error")
        
        # Check server status
        status = check_server_status("http://localhost:8000")
        
        # Verify it returns False for connection error
        self.assertFalse(status)


if __name__ == "__main__":
    unittest.main()