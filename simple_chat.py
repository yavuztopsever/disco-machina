#!/usr/bin/env python3
"""
Simplified chat client for the Project Manager agent.

Part of the Disco-Machina terminal client project.
Created by Yavuz Topsever (https://github.com/yavuztopsever)
"""

import requests
import json
import os
import time
import sys

def simple_chat():
    """Simple chat with the Project Manager agent"""
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
        except EOFError:
            print("\nEOF detected. Exiting...")
            break
        except KeyboardInterrupt:
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
    simple_chat()