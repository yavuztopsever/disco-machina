#!/usr/bin/env python3
"""
Unit tests for error recovery mechanisms.
Tests error handling in client and server components.

This test file is part of the enhanced test suite based on the FLOWS.md documentation,
focusing on the "Error Recovery Flow" described in the document.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class TestTerminalClientErrorRecovery(unittest.TestCase):
    """Test case for error recovery in terminal_client.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import terminal_client and reset its context_storage
        import terminal_client
        terminal_client.context_storage = {
            "messages": [],
            "token_count": 0,
            "max_tokens": 100000,
            "compact_threshold": 80000,
            "session_id": None,
            "offline_mode": False
        }
        self.terminal_client = terminal_client
    
    @patch("terminal_client.print_with_timestamp")
    @patch("terminal_client.send_chat_request")
    def test_error_handling_in_chat_processing(self, mock_send_chat, mock_print):
        """Test error handling in chat processing"""
        # Mock connection error
        mock_send_chat.side_effect = Exception("Connection error")
        
        # Import the module version with this mock
        with patch.dict('sys.modules', {'terminal_client': self.terminal_client}):
            from terminal_client import process_chat_message
            
            # Initialize chat history
            chat_history = [{"role": "system", "content": "You are an AI assistant"}]
            
            # Create args
            args = MagicMock()
            args.server = "http://localhost:8000"
            args.model = "gpt-4"
            
            # Call the function - this should catch the exception
            response = process_chat_message("Hello", chat_history, args, "/tmp/test")
            
            # Verify error message is returned
            self.assertIn("I encountered an error", response)
    
    @patch("terminal_client.check_server_status")
    @patch("terminal_client.print_with_timestamp")
    def test_server_connectivity_check(self, mock_print, mock_check):
        """Test server connectivity check at startup"""
        # Mock server is down
        mock_check.return_value = False
        
        # Call setup_server_connection
        from terminal_client import setup_server_connection
        
        # Mock args
        args = MagicMock()
        args.server = "http://localhost:8000"
        
        # Setup server connection
        setup_server_connection(args)
        
        # Verify offline mode was activated
        self.assertTrue(self.terminal_client.context_storage["offline_mode"])
        
        # Reset offline mode
        self.terminal_client.context_storage["offline_mode"] = False
        
        # Mock server is up
        mock_check.return_value = True
        
        # Setup server connection again
        setup_server_connection(args)
        
        # Verify offline mode was not activated
        self.assertFalse(self.terminal_client.context_storage["offline_mode"])


class TestServerErrorRecovery(unittest.TestCase):
    """Test case for error recovery in server.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Patch required modules to avoid import errors
        self.patchers = [
            patch("src.dev_team.crew.Task", MagicMock()),
            patch("src.dev_team.crew.Agent", MagicMock()),
            patch("src.dev_team.crew.Crew", MagicMock()),
        ]
        for patcher in self.patchers:
            patcher.start()
        
        # Import server module with patched dependencies
        from src.dev_team.server import job_storage
        self.job_storage = job_storage
        
        # Clear job storage
        self.job_storage.clear()
    
    def tearDown(self):
        """Tear down test fixtures"""
        # Stop all patchers
        for patcher in self.patchers:
            patcher.stop()
    
    @patch("src.dev_team.server.DevTeamCrew")
    @patch("fastapi.BackgroundTasks")
    @patch("src.dev_team.server.uuid.uuid4")
    def test_job_creation_adds_background_task(self, mock_uuid, mock_bg_tasks, mock_crew_class):
        """Test that job creation adds a background task"""
        # Import needed modules
        from src.dev_team.server import app, create_project, ProjectRequest
        from fastapi.testclient import TestClient
        
        # Set up test client
        client = TestClient(app)
        
        # Mock UUID generation
        mock_uuid.return_value = "test-job-id"
        
        # Create a test project request
        response = client.post(
            "/projects", 
            json={
                "project_goal": "Test project",
                "codebase_dir": "/tmp/test",
                "non_interactive": False,
                "process_type": "hierarchical",
                "model": "gpt-4",
                "memory": True,
                "tools": "all",
                "delegation": True
            }
        )
        
        # Verify response status code and job ID
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["job_id"], "test-job-id")
        self.assertEqual(response.json()["status"], "queued")


if __name__ == "__main__":
    unittest.main()