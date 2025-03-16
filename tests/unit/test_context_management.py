#!/usr/bin/env python3
"""
Unit tests for context management.
Tests the context compaction and token tracking functionality.

This test file is part of the enhanced test suite based on the FLOWS.md documentation,
focusing on the "Context Management Flow" described in the document.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class TestContextManagement(unittest.TestCase):
    """Test case for context management in terminal client"""
    
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
    
    @patch("terminal_client.print")
    def test_print_with_timestamp(self, mock_print):
        """Test that print_with_timestamp adds messages to context storage"""
        # Call print_with_timestamp multiple times
        self.terminal_client.print_with_timestamp("Test message 1", "info")
        self.terminal_client.print_with_timestamp("Test message 2", "error")
        self.terminal_client.print_with_timestamp("Test message 3", "warning")
        
        # Verify messages were added to context_storage
        self.assertEqual(len(self.terminal_client.context_storage["messages"]), 3)
        self.assertEqual(self.terminal_client.context_storage["messages"][0]["content"], "Test message 1")
        self.assertEqual(self.terminal_client.context_storage["messages"][0]["type"], "info")
        self.assertEqual(self.terminal_client.context_storage["messages"][1]["content"], "Test message 2")
        self.assertEqual(self.terminal_client.context_storage["messages"][1]["type"], "error")
        self.assertEqual(self.terminal_client.context_storage["messages"][2]["content"], "Test message 3")
        self.assertEqual(self.terminal_client.context_storage["messages"][2]["type"], "warning")
        
        # Verify token count was incremented
        self.assertTrue(self.terminal_client.context_storage["token_count"] > 0)
    
    @patch("terminal_client.print")
    @patch("terminal_client.compact_context")
    def test_token_threshold_triggers_compaction(self, mock_compact, mock_print):
        """Test that reaching token threshold triggers compaction"""
        # Set a lower threshold for testing
        self.terminal_client.context_storage["compact_threshold"] = 10
        
        # Call print_with_timestamp with a long message
        self.terminal_client.print_with_timestamp("This is a long message that should exceed the token threshold", "info")
        
        # Verify compact_context was called
        mock_compact.assert_called_once()
    
    @patch("terminal_client.print")
    def test_manual_compaction(self, mock_print):
        """Test manual compaction of context"""
        # Add several messages to context
        for i in range(20):
            self.terminal_client.context_storage["messages"].append({
                "timestamp": "2023-01-01T00:00:00",
                "content": f"Message {i}",
                "type": "info"
            })
            self.terminal_client.context_storage["token_count"] += 5  # Simulate token count
        
        # Store original message count and token count
        original_message_count = len(self.terminal_client.context_storage["messages"])
        original_token_count = self.terminal_client.context_storage["token_count"]
        
        # Call compact_context
        self.terminal_client.compact_context()
        
        # Verify context was compacted
        self.assertLess(len(self.terminal_client.context_storage["messages"]), original_message_count)
        self.assertLess(self.terminal_client.context_storage["token_count"], original_token_count)
        
        # Verify summary message was added
        self.assertEqual(self.terminal_client.context_storage["messages"][0]["type"], "system")
        self.assertIn("SUMMARY", self.terminal_client.context_storage["messages"][0]["content"])
    
    def test_chat_history_compaction(self):
        """Test chat history compaction"""
        # Create a test chat history
        system_message = {"role": "system", "content": "You are an AI assistant"}
        chat_history = [system_message]
        
        # Add several messages to chat history
        for i in range(25):  # Add enough messages to trigger compaction
            chat_history.append({"role": "user", "content": f"User message {i}"})
            chat_history.append({"role": "assistant", "content": f"Assistant response {i}"})
        
        # Store original length
        original_length = len(chat_history)
        
        # Call compact_chat_history
        self.terminal_client.compact_chat_history(chat_history)
        
        # Verify chat history was compacted
        self.assertLess(len(chat_history), original_length)
        
        # Verify system message was preserved at the beginning
        self.assertEqual(chat_history[0], system_message)
        
        # Verify a summary message was added
        self.assertEqual(chat_history[1]["role"], "system")
        self.assertIn("Previous conversation summary", chat_history[1]["content"])
        
        # Verify recent messages were preserved
        self.assertGreaterEqual(len(chat_history), 12)  # 1 system message + 1 summary + 10 recent messages
    
    def test_update_chat_history(self):
        """Test update_chat_history with automatic compaction"""
        # Create a test chat history with system message
        chat_history = [{"role": "system", "content": "You are an AI assistant"}]
        
        # Call update_chat_history multiple times
        for i in range(15):  # Should exceed the compaction threshold
            self.terminal_client.update_chat_history(
                chat_history,
                f"User message {i}",
                f"Assistant response {i}"
            )
        
        # Verify messages were added
        self.assertGreater(len(chat_history), 1)
        
        # With our implementation, compaction should happen automatically
        # after adding enough messages
        self.assertLess(len(chat_history), 31)  # 1 + 15*2
        
        # Verify system message is still at the beginning
        self.assertEqual(chat_history[0]["role"], "system")
        
        # Verify most recent message is from assistant
        self.assertEqual(chat_history[-1]["role"], "assistant")
        self.assertEqual(chat_history[-1]["content"], "Assistant response 14")


if __name__ == "__main__":
    unittest.main()