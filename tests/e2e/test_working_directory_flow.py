#!/usr/bin/env python3
"""
End-to-end tests for the working directory-based operation flow.
Tests the functionality of using the current directory as context.

This test file is part of the enhanced test suite based on the FLOWS.md documentation,
focusing on the "Working Directory Based Operation" flow.
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


@patch("requests.post")
@patch("requests.get")
class TestWorkingDirectoryFlow(unittest.TestCase):
    """Test case for working directory-based operation flow"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create a mock project structure
        os.makedirs(os.path.join(self.temp_dir, "src"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "tests"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "docs"), exist_ok=True)
        
        # Create some files
        with open(os.path.join(self.temp_dir, "README.md"), "w") as f:
            f.write("# Test Project\n\nThis is a test project for testing.")
        
        with open(os.path.join(self.temp_dir, ".env"), "w") as f:
            f.write("API_KEY=test123")
        
        with open(os.path.join(self.temp_dir, "requirements.txt"), "w") as f:
            f.write("fastapi==0.68.0\nuvicorn==0.15.0\n")
        
        with open(os.path.join(self.temp_dir, "src", "main.py"), "w") as f:
            f.write('def main():\n    print("Hello, world!")\n\nif __name__ == "__main__":\n    main()')

    def tearDown(self):
        """Tear down test fixtures"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)

    def test_workspace_info_generation(self, mock_get, mock_post):
        """Test workspace info generation from current directory"""
        # Import get_workspace_info directly
        from terminal_client import get_workspace_info
        
        # Get workspace info
        workspace_info = get_workspace_info()
        
        # Verify workspace info contains correct details
        self.assertEqual(os.path.basename(workspace_info["path"]), os.path.basename(self.temp_dir))
        self.assertEqual(workspace_info["name"], os.path.basename(self.temp_dir))
        self.assertIn("README.md", workspace_info["config_files"])
        self.assertIn("requirements.txt", workspace_info["config_files"])
        # .env is in the list of config files in get_workspace_info, not general files
        self.assertIn(".env", workspace_info["config_files"])
        self.assertIn("src", workspace_info["directories"])
        self.assertIn("tests", workspace_info["directories"])
        self.assertIn("docs", workspace_info["directories"])
    
    def test_directory_resolution(self, mock_get, mock_post):
        """Test directory resolution with current directory as default"""
        # Import resolve_workspace_path directly
        from terminal_client import resolve_workspace_path
        
        # Call without argument (should use current directory)
        workspace_path = resolve_workspace_path()
        
        # Verify it returns the current directory - normalize paths by removing /private prefix on macOS
        real_temp_dir = os.path.normpath(os.path.realpath(self.temp_dir)).replace('/private', '')
        real_workspace_path = os.path.normpath(os.path.realpath(workspace_path)).replace('/private', '')
        self.assertEqual(real_workspace_path, real_temp_dir)
        
        # Create a nested directory
        nested_dir = os.path.join(self.temp_dir, "nested")
        os.makedirs(nested_dir)
        
        # Test with relative path
        rel_path = "nested"
        workspace_path = resolve_workspace_path(rel_path)
        real_nested_dir = os.path.normpath(os.path.realpath(nested_dir)).replace('/private', '')
        real_workspace_path = os.path.normpath(os.path.realpath(workspace_path)).replace('/private', '')
        self.assertEqual(real_workspace_path, real_nested_dir)
        
        # Test with absolute path
        workspace_path = resolve_workspace_path(nested_dir)
        real_workspace_path = os.path.normpath(os.path.realpath(workspace_path)).replace('/private', '')
        self.assertEqual(real_workspace_path, real_nested_dir)
    
    def test_chat_history_initialization(self, mock_get, mock_post):
        """Test chat history initialization with workspace context"""
        # Import initialize_chat_history directly
        from terminal_client import initialize_chat_history
        
        # Initialize chat history with current directory
        chat_history = initialize_chat_history(self.temp_dir)
        
        # Verify chat history contains system message with workspace context
        self.assertEqual(len(chat_history), 1)
        self.assertEqual(chat_history[0]["role"], "system")
        
        # Verify system message contains workspace info
        system_message = chat_history[0]["content"]
        self.assertIn(self.temp_dir, system_message)
        self.assertIn(os.path.basename(self.temp_dir), system_message)
        self.assertIn("README.md", system_message)
        self.assertIn("src", system_message)
        self.assertIn("tests", system_message)
    
    def test_project_creation_with_current_directory(self, mock_get, mock_post):
        """Test project creation using current directory"""
        # Import create_project and set up mocks
        from terminal_client import create_project
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "job_id": "test-uuid",
            "status": "queued",
            "message": "Project creation queued successfully"
        }
        mock_post.return_value = mock_response
        
        # Mock args
        args = MagicMock()
        args.server = "http://localhost:8000"
        args.goal = "Analyze this project"
        args.dir = None  # This should trigger using the current directory
        args.interactive = True
        args.process = "hierarchical"
        args.model = "gpt-4"
        args.memory = True
        args.tools = "all"
        
        # Call create_project
        create_project(args)
        
        # Verify POST request was made with current directory
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        self.assertEqual(call_args["json"]["project_goal"], "Analyze this project")
        
        # Normalize paths for comparison
        expected_dir = os.path.normpath(os.path.realpath(self.temp_dir)).replace('/private', '')
        actual_dir = os.path.normpath(os.path.realpath(call_args["json"]["codebase_dir"])).replace('/private', '')
        self.assertEqual(actual_dir, expected_dir)
        
        self.assertEqual(call_args["json"]["process_type"], "hierarchical")
        self.assertEqual(call_args["json"]["model"], "gpt-4")
        self.assertEqual(call_args["json"]["memory"], True)
        self.assertEqual(call_args["json"]["tools"], "all")
    
    def test_chat_session_with_workspace_context(self, mock_get, mock_post):
        """Test chat session with workspace context"""
        # Mock successful health check
        mock_health_response = MagicMock()
        mock_health_response.status_code = 200
        mock_get.return_value = mock_health_response
        
        # Mock successful chat response
        mock_chat_response = MagicMock()
        mock_chat_response.status_code = 200
        mock_chat_response.json.return_value = {
            "response": "This is a test response based on the workspace context."
        }
        mock_post.return_value = mock_chat_response
        
        # Patch get_user_input to simulate user input
        with patch("terminal_client.get_user_input") as mock_input:
            # Setup input sequence: one chat message, then exit
            mock_input.side_effect = ["Tell me about this project", "exit"]
            
            # Patch display functions to avoid output
            with patch("terminal_client.display_welcome_message"), \
                 patch("terminal_client.display_agent_response"), \
                 patch("terminal_client.display_goodbye_message"), \
                 patch("terminal_client.print_with_timestamp"):
                
                # Import chat_with_agent
                from terminal_client import chat_with_agent
                
                # Mock args
                args = MagicMock()
                args.server = "http://localhost:8000"
                args.model = "gpt-4"
                args.dir = None  # Use current directory
                args.memory = True
                
                # Run chat session
                chat_with_agent(args)
                
                # Verify POST request was made with workspace context
                mock_post.assert_called_once()
                call_args = mock_post.call_args[1]
                request_data = call_args["json"]
                
                # Check that the user message was sent
                self.assertEqual(len(request_data["messages"]), 2)  # System message + user message
                self.assertEqual(request_data["messages"][1]["role"], "user")
                self.assertEqual(request_data["messages"][1]["content"], "Tell me about this project")
                
                # Check that workspace context was included
                self.assertIn("workspace_context", request_data)
                self.assertEqual(request_data["workspace_context"]["name"], os.path.basename(self.temp_dir))
                
                # Normalize paths for comparison
                expected_dir = os.path.normpath(os.path.realpath(self.temp_dir)).replace('/private', '')
                current_dir = os.path.normpath(os.path.realpath(request_data["current_dir"])).replace('/private', '')
                self.assertEqual(current_dir, expected_dir)


if __name__ == "__main__":
    unittest.main()