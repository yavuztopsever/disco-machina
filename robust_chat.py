#!/usr/bin/env python3
"""
Robust chat client for the Project Manager agent.
Works in most terminal environments including restricted ones.

Part of the Disco-Machina terminal client project.
Created by Yavuz Topsever (https://github.com/yavuztopsever)
"""

import requests
import json
import os
import time
import sys
import random

def is_interactive():
    """Check if we're running in an interactive terminal"""
    return hasattr(sys.stdin, 'isatty') and sys.stdin.isatty()

def simulate_chat():
    """Simulate a chat with predefined messages when in non-interactive mode"""
    server_url = "http://localhost:8000"
    codebase_dir = os.getcwd()
    
    print("=" * 60)
    print("Project Manager Agent Chat (SIMULATION MODE)")
    print("=" * 60)
    print(f"Codebase directory: {codebase_dir}")
    print("Running in non-interactive mode. Simulating conversation.\n")
    
    # Predefined user messages to simulate
    user_messages = [
        "What is this project about?",
        "Show me the main components of the architecture",
        "What does the API server do?",
        "Thanks for your help"
    ]
    
    # Initialize chat history
    chat_history = [
        {
            "role": "system", 
            "content": f"You are the Project Manager agent for a software development team. You're helping with a codebase at {codebase_dir}."
        }
    ]
    
    print("[Project Manager] How can I help you with this codebase?\n")
    
    # Simulate exchange
    for message in user_messages:
        # Display simulated user message
        print(f"[Simulated User] {message}")
        
        # Add to chat history
        chat_history.append({"role": "user", "content": message})
        
        try:
            # Show typing indicator
            sys.stdout.write("[Project Manager] ")
            for _ in range(3):
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(0.5)
            
            sys.stdout.write("\r[Project Manager] ")
            sys.stdout.flush()
            
            # Prepare request
            chat_data = {
                "messages": chat_history,
                "codebase_dir": codebase_dir
            }
            
            # Send request to server
            response = requests.post(f"{server_url}/chat", json=chat_data, timeout=30)
            
            if response.status_code == 200:
                agent_response = response.json().get("response", "Sorry, I couldn't process your request.")
                print(agent_response)
                
                # Add to chat history
                chat_history.append({"role": "assistant", "content": agent_response})
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print()  # Add spacing between exchanges
        time.sleep(1)  # Pause between messages
    
    print("\nSimulation complete! This demonstrates the chat functionality.")

def robust_chat():
    """Robust chat with the Project Manager agent"""
    # Check if we're in an interactive terminal
    if not is_interactive():
        print("Not running in an interactive terminal. Switching to simulation mode.")
        simulate_chat()
        return
    
    server_url = "http://localhost:8000"
    codebase_dir = os.getcwd()
    
    print("=" * 60)
    print("Project Manager Agent Chat")
    print("=" * 60)
    print(f"Codebase directory: {codebase_dir}")
    print("Type 'exit' to quit.")
    print("=" * 60)
    
    # Initialize chat history with system message
    chat_history = [
        {
            "role": "system", 
            "content": f"You are the Project Manager agent for a software development team. You're helping with a codebase located at {codebase_dir}. Provide helpful, concise responses."
        }
    ]
    
    # First greeting
    print("\n[Project Manager] How can I help you with this codebase? You can ask me questions or give me tasks.")
    
    # Main chat loop
    while True:
        # Get user input
        try:
            user_input = input("\n[You] ")
        except (EOFError, KeyboardInterrupt):
            print("\nChat interrupted. Exiting...")
            break
            
        # Exit condition
        if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
            print("\nEnding chat session. Goodbye!")
            break
        
        # Add to chat history
        chat_history.append({"role": "user", "content": user_input})
        
        try:
            # Show typing indicator
            sys.stdout.write("[Project Manager] ")
            sys.stdout.flush()
            
            for _ in range(3):
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(0.3)
                
            sys.stdout.write("\r[Project Manager] " + " " * 20 + "\r[Project Manager] ")
            sys.stdout.flush()
            
            # Prepare request
            chat_data = {
                "messages": chat_history,
                "codebase_dir": codebase_dir
            }
            
            # Send request to server
            response = requests.post(f"{server_url}/chat", json=chat_data, timeout=30)
            
            if response.status_code == 200:
                agent_response = response.json().get("response", "Sorry, I couldn't process your request.")
                print(agent_response)
                
                # Add to chat history
                chat_history.append({"role": "assistant", "content": agent_response})
            else:
                print(f"Error: {response.status_code}")
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                    print(f"Server says: {error_detail}")
                except:
                    print(f"Response: {response.text}")
                    
        except requests.exceptions.Timeout:
            print("Request timed out. Server is taking too long to respond.")
        except requests.exceptions.ConnectionError:
            print("Connection error. Server might be down or unreachable.")
        except Exception as e:
            print(f"Error: {str(e)}")
            
            # Offer retry option
            try:
                retry = input("\nWould you like to retry? (y/n): ")
                if retry.lower() != 'y':
                    break
                # Remove the last user message before retry
                if chat_history and chat_history[-1]["role"] == "user":
                    chat_history.pop()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                break

if __name__ == "__main__":
    robust_chat()