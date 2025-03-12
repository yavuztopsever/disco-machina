#!/usr/bin/env python3
"""
Disco-Machina - Terminal client for interacting with Dev Team API server
with real-time output and context management.

Created by Yavuz Topsever (https://github.com/yavuztopsever)
"""

import requests
import json
import time
import sys
import os
import argparse
import threading
import logging
import signal
import pkg_resources
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("discomachina")

# Global variables for context management
context_storage = {
    "messages": [],
    "token_count": 0,
    "max_tokens": 100000,  # Adjust based on model's context window
    "compact_threshold": 80000  # 80% of max tokens
}

# ASCII Art for intro with ANSI colors
ASCII_INTRO = r"""
\033[38;5;51m╔══════════════════════════════════════════════════════════════════════════╗\033[0m
\033[38;5;51m║ \033[38;5;205m                                                                      \033[38;5;51m ║\033[0m
\033[38;5;51m║ \033[38;5;205m  ____  _                 __  __            _     _             \033[38;5;51m ║\033[0m
\033[38;5;51m║ \033[38;5;205m |  _ \(_)___  ___ ___   |  \/  | __ _  ___| |__ (_)_ __   __ _ \033[38;5;51m ║\033[0m
\033[38;5;51m║ \033[38;5;205m | | | | / __|/ __/ _ \  | |\/| |/ _` |/ __| '_ \| | '_ \ / _` |\033[38;5;51m ║\033[0m
\033[38;5;51m║ \033[38;5;76m | |_| | \__ \ (_| (_) | | |  | | (_| | (__| | | | | | | | (_| |\033[38;5;51m ║\033[0m
\033[38;5;51m║ \033[38;5;76m |____/|_|___/\___\___/  |_|  |_|\__,_|\___|_| |_|_|_| |_|\__,_|\033[38;5;51m ║\033[0m
\033[38;5;51m║ \033[38;5;76m                                                                \033[38;5;51m ║\033[0m
\033[38;5;51m║                                                                              ║\033[0m
\033[38;5;51m║ \033[1;38;5;226m                 AI-Powered Dev Team Agents                          \033[38;5;51m ║\033[0m
\033[38;5;51m║ \033[1;38;5;226m          Building the Future, One Line at a Time                    \033[38;5;51m ║\033[0m
\033[38;5;51m║                                                                              ║\033[0m
\033[38;5;51m╚══════════════════════════════════════════════════════════════════════════════╝\033[0m

\033[38;5;93m              ⚪ Create ⚪ Analyze ⚪ Refactor ⚪ Test ⚪ Document               \033[0m
"""

# Function to detect if terminal supports colors
def supports_color():
    """
    Returns True if the running system's terminal supports color,
    and False otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    
    # isatty is not always implemented, so we use try-except
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    if not supported_platform or not is_a_tty:
        return False
        
    return True

# ASCII Art without colors as fallback
ASCII_INTRO_NO_COLOR = r"""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ____  _                 __  __            _     _                      ║
║  |  _ \(_)___  ___ ___   |  \/  | __ _  ___| |__ (_)_ __   __ _         ║
║  | | | | / __|/ __/ _ \  | |\/| |/ _` |/ __| '_ \| | '_ \ / _` |        ║
║  | |_| | \__ \ (_| (_) | | |  | | (_| | (__| | | | | | | | (_| |        ║
║  |____/|_|___/\___\___/  |_|  |_|\__,_|\___|_| |_|_|_| |_|\__,_|        ║
║                                                                          ║
║                                                                          ║
║                  AI-Powered Dev Team Agents                              ║
║           Building the Future, One Line at a Time                        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

               ⚪ Create ⚪ Analyze ⚪ Refactor ⚪ Test ⚪ Document
"""

def print_with_timestamp(message, message_type="info"):
    """Print message with timestamp and track in context storage
    
    message_type can be:
    - "info" (default): regular information
    - "success": success messages
    - "error": error messages
    - "warning": warning messages
    - "system": system messages
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Color selection based on message type
    if supports_color():
        color_codes = {
            "info": "\033[38;5;39m",  # Light blue
            "success": "\033[38;5;76m",  # Green
            "error": "\033[38;5;196m",  # Red
            "warning": "\033[38;5;208m",  # Orange
            "system": "\033[38;5;93m",  # Purple
        }
        
        time_color = "\033[38;5;245m"  # Gray for timestamp
        reset = "\033[0m"
        
        color = color_codes.get(message_type, color_codes["info"])
        print(f"{time_color}[{timestamp}]{reset} {color}{message}{reset}")
    else:
        # Fallback to plain text
        print(f"[{timestamp}] {message}")
    
    # Store message in context
    context_storage["messages"].append({
        "timestamp": timestamp,
        "content": message,
        "type": message_type
    })
    
    # Approximate token count (rough estimate: 4 chars ≈ 1 token)
    context_storage["token_count"] += (len(message) // 4)
    
    # Check if compaction is needed
    if context_storage["token_count"] >= context_storage["compact_threshold"]:
        compact_context()

def compact_context():
    """Compact the context by summarizing older messages"""
    if supports_color():
        print(f"\n\033[38;5;93m====== COMPACTING CONTEXT ======\033[0m")
        print(f"\033[38;5;93mContext window approaching limit. Summarizing older messages...\033[0m")
    else:
        print("\n====== COMPACTING CONTEXT ======")
        print("Context window approaching limit. Summarizing older messages...")
    
    # Keep the 20% most recent messages
    keep_count = max(len(context_storage["messages"]) // 5, 10)  # At least keep 10 messages
    
    # Summarize older messages
    older_messages = context_storage["messages"][:-keep_count]
    recent_messages = context_storage["messages"][-keep_count:]
    
    # Create a summary of older messages
    summary = f"[SUMMARY: {len(older_messages)} previous messages compacted]"
    
    # Reset context with summary and recent messages
    context_storage["messages"] = [{"timestamp": "SUMMARY", "content": summary, "type": "system"}] + recent_messages
    
    # Recalculate token count (rough estimate)
    context_storage["token_count"] = sum(len(m["content"]) // 4 for m in context_storage["messages"])
    
    if supports_color():
        print(f"\033[38;5;93mContext compacted. New token count: ~{int(context_storage['token_count'])}\033[0m")
        print(f"\033[38;5;93m====== COMPACTION COMPLETE ======\033[0m\n")
    else:
        print(f"Context compacted. New token count: ~{int(context_storage['token_count'])}")
        print("====== COMPACTION COMPLETE ======\n")

def monitor_job(job_id, server_url, interval=2):
    """Monitor job progress and stream output"""
    print_with_timestamp(f"Monitoring job {job_id}", "system")
    
    while True:
        try:
            response = requests.get(f"{server_url}/projects/{job_id}")
            if response.status_code == 200:
                job_data = response.json()
                status = job_data.get("status")
                
                if status == "completed":
                    print_with_timestamp(f"Job completed successfully! 🎉", "success")
                    result = job_data.get("result", {})
                    
                    # Pretty print the result with colors if supported
                    if supports_color():
                        formatted_json = json.dumps(result, indent=2)
                        # Basic JSON syntax highlighting
                        formatted_json = formatted_json.replace('{', '\033[38;5;208m{\033[0m')
                        formatted_json = formatted_json.replace('}', '\033[38;5;208m}\033[0m')
                        formatted_json = formatted_json.replace('[', '\033[38;5;208m[\033[0m')
                        formatted_json = formatted_json.replace(']', '\033[38;5;208m]\033[0m')
                        formatted_json = formatted_json.replace(':', '\033[38;5;208m:\033[0m')
                        print(formatted_json)
                    else:
                        print(json.dumps(result, indent=2))
                    break
                elif status == "failed":
                    print_with_timestamp("Job failed! ❌", "error")
                    error = job_data.get("result", {}).get("error", "Unknown error")
                    print_with_timestamp(f"Error: {error}", "error")
                    break
                else:
                    # Still running, show status update with rotating indicator
                    indicators = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
                    indicator = indicators[int(time.time()) % len(indicators)]
                    print_with_timestamp(f"Job status: {status} {indicator}", "info")
            else:
                print_with_timestamp(f"Error checking job status: {response.status_code}", "error")
                print_with_timestamp(response.text, "error")
                break
        except Exception as e:
            print_with_timestamp(f"Error monitoring job: {str(e)}", "error")
            break
            
        time.sleep(interval)

def manually_compact():
    """Manually trigger context compaction"""
    if context_storage["messages"]:
        print_with_timestamp("Manually triggering context compaction...", "system")
        compact_context()
    else:
        print_with_timestamp("No context to compact yet.", "warning")

def create_project(args):
    """Create a new project"""
    url = f"{args.server}/projects"
    
    # Use current directory if not specified
    codebase_dir = args.dir if args.dir else os.getcwd()
    
    data = {
        "project_goal": args.goal,
        "codebase_dir": codebase_dir,
        "non_interactive": not args.interactive
    }
    
    print_with_timestamp(f"Creating project with goal: {args.goal}", "info")
    print_with_timestamp(f"Using codebase directory: {codebase_dir}", "info")
    
    interactive_mode = "🔄 Interactive" if args.interactive else "⏩ Non-interactive"
    print_with_timestamp(f"Mode: {interactive_mode}", "info")
    
    # Animate "Creating project" message
    if supports_color():
        print("\033[38;5;205m", end="")
        print("Initializing Dev Team agents...", end="", flush=True)
        for _ in range(5):
            time.sleep(0.3)
            print(".", end="", flush=True)
        print("\033[0m")
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            job_data = response.json()
            job_id = job_data.get("job_id")
            print_with_timestamp(f"Project created with job ID: {job_id}", "success")
            
            # Monitor the job progress
            monitor_job(job_id, args.server)
        else:
            print_with_timestamp(f"Error creating project: {response.status_code}", "error")
            print_with_timestamp(response.text, "error")
    except Exception as e:
        print_with_timestamp(f"Error: {str(e)}", "error")

def list_projects(args):
    """List all projects"""
    url = f"{args.server}/projects"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            projects = response.json()
            if not projects:
                print_with_timestamp("No projects found")
            else:
                print_with_timestamp(f"Found {len(projects)} projects:")
                for project in projects:
                    print(f"Job ID: {project.get('job_id')}")
                    print(f"Status: {project.get('status')}")
                    print(f"Goal: {project.get('project_goal')}")
                    print(f"Created: {project.get('created_at')}")
                    print("-" * 50)
        else:
            print_with_timestamp(f"Error listing projects: {response.status_code}")
            print(response.text)
    except Exception as e:
        print_with_timestamp(f"Error: {str(e)}")

def get_project(args):
    """Get project status"""
    url = f"{args.server}/projects/{args.job_id}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            project = response.json()
            print(f"Job ID: {project.get('job_id')}")
            print(f"Status: {project.get('status')}")
            print(f"Goal: {project.get('project_goal')}")
            print(f"Created: {project.get('created_at')}")
            print(f"Updated: {project.get('updated_at')}")
            
            result = project.get('result')
            if result:
                print("\nResult:")
                print(json.dumps(result, indent=2))
        else:
            print_with_timestamp(f"Error getting project: {response.status_code}")
            print(response.text)
    except Exception as e:
        print_with_timestamp(f"Error: {str(e)}")

def replay_task(args):
    """Replay a specific task"""
    url = f"{args.server}/tasks/replay"
    
    data = {
        "task_index": args.index
    }
    
    print_with_timestamp(f"Replaying task with index: {args.index}")
    try:
        response = requests.post(url, json=data)
        if response.status_code == 202:
            job_data = response.json()
            job_id = job_data.get("job_id")
            print_with_timestamp(f"Task replay queued with job ID: {job_id}")
            
            # Monitor the job progress
            monitor_job(job_id, args.server)
        else:
            print_with_timestamp(f"Error replaying task: {response.status_code}")
            print(response.text)
    except Exception as e:
        print_with_timestamp(f"Error: {str(e)}")

def reset_memory(args):
    """Reset memory"""
    url = f"{args.server}/memory/reset"
    
    data = {
        "memory_type": args.type
    }
    
    print_with_timestamp(f"Resetting {args.type} memory", "warning")
    try:
        response = requests.post(url, json=data)
        if response.status_code == 202:
            print_with_timestamp(f"Memory reset successful", "success")
            print_with_timestamp(response.json().get("message"), "info")
        else:
            print_with_timestamp(f"Error resetting memory: {response.status_code}", "error")
            print_with_timestamp(response.text, "error")
    except Exception as e:
        print_with_timestamp(f"Error: {str(e)}", "error")
        
def chat_with_agent(args):
    """Start an interactive chat with the Project Manager agent"""
    url = f"{args.server}/chat"
    codebase_dir = os.getcwd()
    
    # Welcome message
    if supports_color():
        print("\n\033[38;5;205m╔══════════════════════════════════════════════════════════════════════════╗\033[0m")
        print("\033[38;5;205m║                      Project Manager Agent Chat                           ║\033[0m")
        print("\033[38;5;205m╚══════════════════════════════════════════════════════════════════════════╝\033[0m\n")
    else:
        print("\n╔══════════════════════════════════════════════════════════════════════════╗")
        print("║                      Project Manager Agent Chat                           ║")
        print("╚══════════════════════════════════════════════════════════════════════════╝\n")
    
    print_with_timestamp("Starting chat session with Project Manager agent...", "system")
    print_with_timestamp("Current codebase: " + codebase_dir, "info")
    
    # Animate connecting to agent
    progress_bar("Connecting to Project Manager agent...", duration=1.5)
    
    # Initialize chat history with system message
    chat_history = [
        {
            "role": "system", 
            "content": f"You are the Project Manager agent for a software development team. You're helping with a codebase located at {codebase_dir}. Provide helpful, concise responses to the user's questions about their project."
        }
    ]
    
    # Add initial message from agent
    initial_agent_message = {
        "role": "assistant",
        "content": "How can I help you today? You can ask questions about your codebase, request research, brainstorm ideas, or give me specific tasks."
    }
    chat_history.append(initial_agent_message)
    
    # Display initial agent message
    if supports_color():
        agent_prompt = f"\033[38;5;76m[Project Manager]\033[0m {initial_agent_message['content']}"
    else:
        agent_prompt = f"[Project Manager] {initial_agent_message['content']}"
    
    print("\n" + agent_prompt + "\n")
    
    # Check server connectivity before starting chat
    try:
        health_check = requests.get(f"{args.server}/health", timeout=5)
        if health_check.status_code != 200:
            print_with_timestamp("Warning: Server appears to be online but may not be responding properly.", "warning")
    except Exception as e:
        print_with_timestamp(f"Warning: Could not connect to server at {args.server}", "warning")
        print_with_timestamp("Chat might not work correctly. Make sure the server is running.", "warning")
    
    # Main chat loop
    while True:
        # Get user input
        if supports_color():
            user_input = input("\033[38;5;39m[You]\033[0m ")
        else:
            user_input = input("[You] ")
        
        # Exit condition
        if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
            print_with_timestamp("Ending chat session. Goodbye!", "success")
            break
        
        # Add to chat history
        chat_history.append({"role": "user", "content": user_input})
        
        try:
            # Prepare request
            chat_data = {
                "messages": chat_history,
                "codebase_dir": codebase_dir
            }
            
            # Add optional model if specified
            if args.model:
                chat_data["model"] = args.model
            
            # Display typing indicator
            if supports_color():
                print("\033[38;5;76m[Project Manager]\033[0m ", end="", flush=True)
                indicators = ['⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽', '⣾']
                for _ in range(3):  # Short animation
                    for indicator in indicators:
                        print(f"\b{indicator}", end="", flush=True)
                        time.sleep(0.1)
                print("\b \b", end="", flush=True)  # Clear the indicator
            
            # Send request to server with appropriate timeout
            response = requests.post(url, json=chat_data, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                agent_response = response_data.get("response", "Sorry, I couldn't process your request.")
                
                # Format and display the response
                if supports_color():
                    print("\033[38;5;76m[Project Manager]\033[0m " + agent_response)
                else:
                    print("[Project Manager] " + agent_response)
                
                # Add to chat history
                chat_history.append({"role": "assistant", "content": agent_response})
                
                # Check if we need to compact
                total_tokens = sum(len(m["content"]) // 4 for m in chat_history)
                if total_tokens > context_storage["compact_threshold"]:
                    # Compact chat history
                    print_with_timestamp("Chat history is getting long. Compacting...", "system")
                    # Keep system message and the most recent 5 exchanges (10 messages)
                    system_message = chat_history[0]  # Save system message
                    chat_history = [system_message] + chat_history[-10:]
                    print_with_timestamp("Chat history compacted. Continuing with recent messages.", "system")
            else:
                # Try to get error message from JSON response
                try:
                    error_msg = response.json().get("detail", f"Error: HTTP {response.status_code}")
                except:
                    error_msg = f"Error: HTTP {response.status_code}"
                
                print_with_timestamp(error_msg, "error")
                print_with_timestamp("The server might be experiencing issues. Please try again later.", "error")
        
        except requests.exceptions.Timeout:
            print_with_timestamp("Request timed out. The server is taking too long to respond.", "error")
        except requests.exceptions.ConnectionError:
            print_with_timestamp("Connection error. The server might be down or unreachable.", "error")
        except Exception as e:
            print_with_timestamp(f"Error communicating with server: {str(e)}", "error")
            
            # Offer fallback options
            print_with_timestamp("Would you like to:", "system")
            print_with_timestamp("1. Retry", "info")
            print_with_timestamp("2. Start a new chat", "info")
            print_with_timestamp("3. Exit", "info")
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == "1":
                # Remove last user message before retry
                if chat_history and chat_history[-1]["role"] == "user":
                    chat_history.pop()
                continue
            elif choice == "2":
                # Keep only the system message
                system_message = chat_history[0]
                chat_history = [system_message, initial_agent_message]
                print_with_timestamp("Starting a new chat session...", "system")
                print("\n" + agent_prompt + "\n")
                continue
            else:
                print_with_timestamp("Ending chat session. Goodbye!", "success")
                break
        
        print()  # Extra line for readability

def check_server_status(server_url):
    """Check if the server is running"""
    try:
        response = requests.get(f"{server_url}/health")
        if response.status_code == 200:
            return True
        return False
    except:
        return False

def progress_bar(title, duration=3, width=30):
    """Display an animated progress bar"""
    if not supports_color():
        return
    
    # Colors
    title_color = "\033[38;5;205m"
    bar_color = "\033[38;5;76m"
    reset = "\033[0m"
    
    print(f"{title_color}{title}{reset}")
    
    # Animation loop
    for i in range(width + 1):
        progress = i / width
        bar = bar_color + "█" * i + "░" * (width - i) + reset
        percent = int(progress * 100)
        
        # Print progress bar
        print(f"\r{bar} {percent}%", end="", flush=True)
        time.sleep(duration / width)
    
    print()  # New line after completion

def setup_keyboard_shortcuts():
    """Setup keyboard shortcuts for the client"""
    # Only available on Unix systems
    if os.name == 'posix':
        # Handle Ctrl+C for graceful exit
        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
        
        # Handle Ctrl+Z for manual compaction (where supported)
        try:
            signal.signal(signal.SIGTSTP, lambda sig, frame: manually_compact())
            if supports_color():
                print("\033[38;5;93mKeyboard shortcuts enabled:\033[0m")
                print("\033[38;5;93m  Ctrl+Z:\033[0m \033[38;5;76mManually compact context\033[0m")
                print("\033[38;5;93m  Ctrl+C:\033[0m \033[38;5;76mExit\033[0m")
            else:
                print("Keyboard shortcuts enabled:")
                print("  Ctrl+Z: Manually compact context")
                print("  Ctrl+C: Exit")
        except:
            pass

def print_version():
    """Print the current version of Disco-Machina"""
    try:
        version = "1.0.0"  # Can be updated dynamically
        if supports_color():
            print(f"\033[38;5;226mDisco-Machina\033[0m \033[38;5;245mversion\033[0m \033[38;5;76m{version}\033[0m")
        else:
            print(f"Disco-Machina version {version}")
    except:
        print("Disco-Machina version unknown")

def main():
    # Create main parser
    parser = argparse.ArgumentParser(description="Disco-Machina - Terminal client for Dev Team API")
    parser.add_argument("--server", default="http://localhost:8000", help="Server URL")
    parser.add_argument("--version", action="store_true", help="Show version information")
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create parser for "create" command
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("--goal", required=True, help="Project goal")
    create_parser.add_argument("--dir", help="Codebase directory (defaults to current directory)")
    create_parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    create_parser.set_defaults(func=create_project)
    
    # Create parser for "list" command
    list_parser = subparsers.add_parser("list", help="List all projects")
    list_parser.set_defaults(func=list_projects)
    
    # Create parser for "get" command
    get_parser = subparsers.add_parser("get", help="Get project status")
    get_parser.add_argument("job_id", help="Job ID")
    get_parser.set_defaults(func=get_project)
    
    # Create parser for "replay" command
    replay_parser = subparsers.add_parser("replay", help="Replay a task")
    replay_parser.add_argument("index", type=int, help="Task index")
    replay_parser.set_defaults(func=replay_task)
    
    # Create parser for "reset" command
    reset_parser = subparsers.add_parser("reset", help="Reset memory")
    reset_parser.add_argument("--type", default="all", help="Memory type to reset (default: all)")
    reset_parser.set_defaults(func=reset_memory)
    
    # Create parser for "compact" command
    compact_parser = subparsers.add_parser("compact", help="Manually compact context")
    compact_parser.set_defaults(func=lambda args: manually_compact())
    
    # Create parser for "chat" command
    chat_parser = subparsers.add_parser("chat", help="Start an interactive chat with the Project Manager agent")
    chat_parser.add_argument("--model", default="", help="Specify AI model to use (if supported)")
    chat_parser.set_defaults(func=chat_with_agent)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Display intro after argument parsing
    # Use colored ASCII art if terminal supports it
    if supports_color():
        # Clear screen for better presentation
        os.system('cls' if os.name == 'nt' else 'clear')
        print(ASCII_INTRO)
    else:
        print(ASCII_INTRO_NO_COLOR)
    
    print_version()
    
    # Show working directory with color coding
    if supports_color():
        cwd = os.getcwd()
        print(f"\033[38;5;245mWorking directory:\033[0m \033[38;5;39m{cwd}\033[0m")
    else:
        print(f"Working directory: {os.getcwd()}")
    
    # Setup keyboard shortcuts
    setup_keyboard_shortcuts()
    
    # Connecting to server animation
    progress_bar("Initializing Disco-Machina...", duration=1.5)
    
    # If version flag is set
    if hasattr(args, 'version') and args.version:
        print_version()
        return
    
    # If no command is provided, show help
    if not args.command:
        # Show a friendly welcome message
        if supports_color():
            print("\n\033[38;5;226mWelcome to Disco-Machina!\033[0m")
            print("\033[38;5;245mTo get started, try one of these commands:\033[0m")
            print("\033[38;5;76m  terminal_client.py create --goal \"Analyze this codebase\" --interactive\033[0m")
            print("\033[38;5;76m  terminal_client.py list\033[0m")
            print("\033[38;5;76m  terminal_client.py chat\033[0m\n")
        else:
            print("\nWelcome to Disco-Machina!")
            print("To get started, try one of these commands:")
            print("  terminal_client.py create --goal \"Analyze this codebase\" --interactive")
            print("  terminal_client.py list")
            print("  terminal_client.py chat\n")
        
        parser.print_help()
        return
    
    # Check if server is running
    try:
        if not check_server_status(args.server):
            print_with_timestamp(f"Warning: Unable to connect to server at {args.server}", "warning")
            print_with_timestamp("Make sure the Dev Team API server is running.", "warning")
            
            if supports_color():
                response = input("\033[38;5;208mDo you want to continue anyway? (y/n): \033[0m")
            else:
                response = input("Do you want to continue anyway? (y/n): ")
                
            if response.lower() != 'y':
                return
        else:
            print_with_timestamp("Connected to Dev Team API server! 🚀", "success")
    except Exception as e:
        print_with_timestamp(f"Error checking server status: {str(e)}", "error")
        print_with_timestamp("Continuing anyway...", "warning")
    
    # Execute the appropriate function
    try:
        args.func(args)
    except Exception as e:
        print_with_timestamp(f"Error executing command: {str(e)}", "error")

if __name__ == "__main__":
    main()