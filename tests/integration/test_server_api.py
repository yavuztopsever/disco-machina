#!/usr/bin/env python3
"""
Integration tests for the server API endpoints.
Tests all new endpoints including train and test.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json
import asyncio
from fastapi.testclient import TestClient

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Import Process directly
from crewai import Process

# Patch Task and other CrewAI classes to avoid validation errors
with patch("src.dev_team.crew.Task", MagicMock()), \
     patch("src.dev_team.crew.Agent", MagicMock()), \
     patch("src.dev_team.crew.Crew", MagicMock()):
    # Now import the app with patched dependencies
    from src.dev_team.server import app, job_storage

# Create a test client
client = TestClient(app)


class TestServerAPI(unittest.TestCase):
    """Test case for the API server endpoints"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        # Clear job storage before each test
        job_storage.clear()

    def tearDown(self):
        """Tear down test fixtures"""
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch("fastapi.BackgroundTasks.add_task")
    @patch("src.dev_team.server.uuid.uuid4")
    def test_create_project_endpoint(self, mock_uuid, mock_add_task):
        """Test the /projects endpoint with CrewAI options"""
        # Mock UUID generation
        mock_uuid.return_value = "test-uuid"
        
        # Test project creation with all CrewAI options
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
        data = response.json()
        self.assertEqual(data["job_id"], "test-uuid")
        self.assertEqual(data["status"], "queued")
        
        # Check that the job was added to storage
        self.assertIn("test-uuid", job_storage)
        self.assertEqual(job_storage["test-uuid"]["project_goal"], "Test goal")
        self.assertEqual(job_storage["test-uuid"]["codebase_dir"], self.temp_dir)
        
        # We don't verify the background task was added since we can't
        # directly mock the fastapi.BackgroundTasks instance used in the endpoint

    @patch("fastapi.BackgroundTasks.add_task")
    @patch("src.dev_team.server.uuid.uuid4")
    def test_replay_task_endpoint(self, mock_uuid, mock_add_task):
        """Test the /tasks/replay endpoint with CrewAI options"""
        # Mock UUID generation
        mock_uuid.return_value = "test-uuid"
        
        # Test task replay with all CrewAI options
        response = client.post(
            "/tasks/replay", 
            json={
                "task_index": 0,
                "process_type": "sequential",
                "model": "gpt-4",
                "memory": True,
                "tools": "RequirementsAnalysisTool,CodeAnalysisTool",
                "verbose": True,
                "with_delegation": True
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 202)
        data = response.json()
        self.assertEqual(data["job_id"], "test-uuid")
        self.assertEqual(data["status"], "queued")
        self.assertEqual(data["task_index"], 0)
        
        # Check that the job was added to storage
        self.assertIn("test-uuid", job_storage)
        self.assertEqual(job_storage["test-uuid"]["task_index"], 0)
        self.assertEqual(job_storage["test-uuid"]["process_type"], "sequential")

    @patch("fastapi.BackgroundTasks.add_task")
    @patch("src.dev_team.server.uuid.uuid4")
    def test_train_endpoint(self, mock_uuid, mock_add_task):
        """Test the /train endpoint with CrewAI options"""
        # Mock UUID generation
        mock_uuid.return_value = "test-uuid"
        
        # Test train with all CrewAI options
        response = client.post(
            "/train", 
            json={
                "project_goal": "Train goal",
                "codebase_dir": self.temp_dir,
                "iterations": 3,
                "output_file": "results.json",
                "process_type": "hierarchical",
                "model": "gpt-4",
                "memory": True,
                "tools": "RequirementsAnalysisTool,CodeAnalysisTool"
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 202)
        data = response.json()
        self.assertEqual(data["job_id"], "test-uuid")
        self.assertEqual(data["status"], "queued")
        self.assertEqual(data["iterations"], 3)
        self.assertEqual(data["output_file"], "results.json")
        
        # Check that the job was added to storage
        self.assertIn("test-uuid", job_storage)
        self.assertEqual(job_storage["test-uuid"]["project_goal"], "Train goal")
        self.assertEqual(job_storage["test-uuid"]["iterations"], 3)

    @patch("fastapi.BackgroundTasks.add_task")
    @patch("src.dev_team.server.uuid.uuid4")
    def test_test_endpoint(self, mock_uuid, mock_add_task):
        """Test the /test endpoint with CrewAI options"""
        # Mock UUID generation
        mock_uuid.return_value = "test-uuid"
        
        # Test the test endpoint with all CrewAI options
        response = client.post(
            "/test", 
            json={
                "project_goal": "Test goal",
                "codebase_dir": self.temp_dir,
                "iterations": 2,
                "model": "gpt-4",
                "process_type": "sequential",
                "memory": True,
                "tools": "RequirementsAnalysisTool,CodeAnalysisTool"
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 202)
        data = response.json()
        self.assertEqual(data["job_id"], "test-uuid")
        self.assertEqual(data["status"], "queued")
        self.assertEqual(data["iterations"], 2)
        self.assertEqual(data["model"], "gpt-4")
        
        # Check that the job was added to storage
        self.assertIn("test-uuid", job_storage)
        self.assertEqual(job_storage["test-uuid"]["project_goal"], "Test goal")
        self.assertEqual(job_storage["test-uuid"]["iterations"], 2)
        self.assertEqual(job_storage["test-uuid"]["model"], "gpt-4")

    def test_chat_endpoint(self):
        """Test the /chat endpoint with memory option"""
        # Mock the DevTeamCrew instance and its process_chat method
        with patch("src.dev_team.server.DevTeamCrew") as mock_crew_class:
            mock_crew_instance = MagicMock()
            mock_crew_class.return_value = mock_crew_instance
            mock_crew_instance.process_chat.return_value = "Test response"
            
            # Test chat with memory option
            response = client.post(
                "/chat", 
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                    "model": "gpt-4",
                    "workspace_context": {"test": "data"},
                    "current_dir": self.temp_dir,
                    "memory": True
                }
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["response"], "Test response")
            
            # Verify DevTeamCrew was created with memory_enabled=True
            mock_crew_class.assert_called_once()
            self.assertEqual(mock_crew_class.call_args[1].get("memory_enabled"), True)
            
            # Verify process_chat was called with correct arguments
            mock_crew_instance.process_chat.assert_called_once_with(
                messages=[{"role": "user", "content": "Hello"}],
                model="gpt-4",
                workspace_context={"test": "data"}
            )

    def test_reset_memory_endpoint(self):
        """Test the /memory/reset endpoint"""
        # Test memory reset
        response = client.post(
            "/memory/reset", 
            json={"memory_type": "all"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 202)
        data = response.json()
        self.assertEqual(data["status"], "success")
        
        # We don't verify DevTeamCrew was created since that's handled
        # by the actual function implementation

    def test_health_endpoint(self):
        """Test the /health endpoint"""
        response = client.get("/health")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("timestamp", data)
        self.assertIn("active_websockets", data)


if __name__ == "__main__":
    unittest.main()