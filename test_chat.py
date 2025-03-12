#!/usr/bin/env python3
"""
Simple test script for the chat functionality with the Project Manager agent.

Part of the Disco-Machina terminal client project.
Created by Yavuz Topsever (https://github.com/yavuztopsever)
"""

import requests
import json
import sys
import os

def test_chat():
    print("Testing chat with Project Manager agent...")
    server_url = "http://localhost:8000"
    
    # Test health check
    try:
        health_response = requests.get(f"{server_url}/health")
        print(f"Health check response: {health_response.status_code}")
        print(f"Health data: {health_response.json()}")
    except Exception as e:
        print(f"Error checking server health: {str(e)}")
        return
    
    # Test chat endpoint
    try:
        # Create a simple message
        messages = [
            {
                "role": "system", 
                "content": "You are the Project Manager agent for a software development team."
            },
            {
                "role": "user",
                "content": "Hello, can you help me understand this codebase?"
            }
        ]
        
        # Create request data
        chat_data = {
            "messages": messages,
            "codebase_dir": os.getcwd()
        }
        
        # Send request
        print(f"Sending chat request with data: {json.dumps(chat_data, indent=2)}")
        chat_response = requests.post(f"{server_url}/chat", json=chat_data, timeout=30)
        
        # Parse response
        print(f"Chat response code: {chat_response.status_code}")
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            print(f"Agent reply: {response_data.get('response')}")
        else:
            print(f"Error response: {chat_response.text}")
    
    except Exception as e:
        print(f"Error testing chat: {str(e)}")

if __name__ == "__main__":
    test_chat()