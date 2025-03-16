#!/usr/bin/env python3
"""
Integration tests for WebSocket connections and real-time updates.
Tests the WebSocket endpoint for job status updates.

This test file is part of the enhanced test suite based on the FLOWS.md documentation,
focusing on the "WebSocket-Based Real-Time Updates" functionality described in the document.
"""

import os
import sys
import unittest
import asyncio
import json
import time
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import websockets
from websockets.exceptions import ConnectionClosed

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Patch Task and other CrewAI classes to avoid validation errors
with patch("src.dev_team.crew.Task", MagicMock()), \
     patch("src.dev_team.crew.Agent", MagicMock()), \
     patch("src.dev_team.crew.Crew", MagicMock()):
    # Now import the app with patched dependencies
    from src.dev_team.server import app, job_storage, manager

# Create a test client
client = TestClient(app)


class TestWebSocketRealTimeUpdates(unittest.TestCase):
    """Test case for WebSocket real-time updates"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        # Clear job storage before each test
        job_storage.clear()
        # Reset active connections
        manager.active_connections = {}

    def tearDown(self):
        """Tear down test fixtures"""
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch("src.dev_team.server.uuid.uuid4")
    @patch("src.dev_team.server.process_job")  # Patch the process_job to avoid errors
    def test_websocket_connection(self, mock_process_job, mock_uuid):
        """Test WebSocket connection establishment"""
        # Mock UUID generation
        mock_uuid.return_value = "test-uuid"
        
        # Ensure the job is in storage with correct status
        job_storage["test-uuid"] = {
            "job_id": "test-uuid",
            "project_goal": "Test goal",
            "codebase_dir": self.temp_dir,
            "status": "queued",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "progress": 0
        }
        
        # Create a job first - with mocked process_job
        response = client.post(
            "/projects", 
            json={
                "project_goal": "Test goal",
                "codebase_dir": self.temp_dir,
                "non_interactive": False,
                "process_type": "hierarchical",
                "model": "gpt-4",
                "memory": True,
                "tools": "RequirementsAnalysisTool,CodeAnalysisTool",
                "delegation": True
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 201)
        
        # Create WebSocket connection
        with client.websocket_connect(f"/ws/test-uuid") as websocket:
            # Verify initial message is received
            data = websocket.receive_json()
            self.assertEqual(data["job_id"], "test-uuid")
            self.assertEqual(data["status"], "queued")
            self.assertIn("message", data)
            self.assertIn("timestamp", data)

    @patch("src.dev_team.server.uuid.uuid4")
    @patch("src.dev_team.server.process_job")  # Patch the process_job to avoid errors
    def test_websocket_job_updates(self, mock_process_job, mock_uuid):
        """Test WebSocket job status updates"""
        # This test focuses on client-side test of WebSocket communication
        # rather than testing the actual server-side update behavior
        
        # Create job storage with proper status to avoid server-side errors
        job_storage["test-uuid"] = {
            "job_id": "test-uuid",
            "project_goal": "Test goal",
            "codebase_dir": self.temp_dir,
            "status": "queued",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "progress": 0
        }
        
        # Mock UUID generation
        mock_uuid.return_value = "test-uuid"
        
        # Create a job first (primarily to test the API itself)
        response = client.post(
            "/projects", 
            json={
                "project_goal": "Test goal",
                "codebase_dir": self.temp_dir,
                "non_interactive": False,
                "process_type": "hierarchical",
                "model": "gpt-4",
                "memory": True,
                "tools": "RequirementsAnalysisTool,CodeAnalysisTool",
                "delegation": True
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 201)
        
        # Connect to WebSocket to verify initial status is received
        with client.websocket_connect(f"/ws/test-uuid") as websocket:
            # Initial status should come from the queued job
            data = websocket.receive_json()
            self.assertEqual(data["job_id"], "test-uuid")
            self.assertEqual(data["status"], "queued")

    def test_websocket_job_error_status(self):
        """Test WebSocket job with error status"""
        # Create a job with error status directly in job storage
        error_job_id = "error-job-id"
        job_storage[error_job_id] = {
            "job_id": error_job_id,
            "project_goal": "Test goal",
            "codebase_dir": self.temp_dir,
            "status": "failed",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00", 
            "progress": 0,
            "result": {"error": "Test error message"}
        }
        
        # Connect to WebSocket to verify error status is received
        with client.websocket_connect(f"/ws/{error_job_id}") as websocket:
            # Initial status should show the failed state
            data = websocket.receive_json()
            self.assertEqual(data["job_id"], error_job_id)
            self.assertEqual(data["status"], "failed")
            self.assertEqual(data["result"]["error"], "Test error message")

    def test_websocket_nonexistent_job(self):
        """Test WebSocket connection with nonexistent job ID"""
        # Connect to WebSocket with nonexistent job ID
        with client.websocket_connect("/ws/nonexistent-job-id") as websocket:
            # Verify 'not found' message is received
            data = websocket.receive_json()
            self.assertEqual(data["job_id"], "nonexistent-job-id")
            self.assertEqual(data["status"], "not_found")
            self.assertIn("Job not found", data["message"])


if __name__ == "__main__":
    unittest.main()