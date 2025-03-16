#!/usr/bin/env python3
"""
Disco-Machina - Terminal client for interacting with API server
with real-time output and context management.

This is a self-contained terminal client that provides:
- Interactive chat with AI agents
- Project management and task tracking
- Offline mode support with graceful degradation
- Robust error handling and recovery
- Context-aware command completion
- Automatic session management

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
import sqlite3
import readline
import atexit
import hashlib
import websocket
import queue
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Version information
__version__ = "1.0.0"
__author__ = "Yavuz Topsever"
__email__ = "yavuz.topsever@windowslive.com"

# Configure logging with rotation
log_file = os.path.join(os.path.expanduser("~"), ".discomachina", "client.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("discomachina")

# Global variables for context management
context_storage = {
    "messages": [],
    "token_count": 0,
    "max_tokens": 100000,  # Adjust based on model's context window
    "compact_threshold": 80000,  # 80% of max tokens
    "session_id": None,
    "offline_mode": False
}

class OfflineCache:
    """Handle offline caching of requests and responses"""
    def __init__(self):
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".discomachina", "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.db_path = os.path.join(self.cache_dir, "offline_cache.db")
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for caching"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    request_hash TEXT PRIMARY KEY,
                    request TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def cache_response(self, request: Dict[str, Any], response: Dict[str, Any]):
        """Cache a response for a given request"""
        request_hash = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (request_hash, request, response) VALUES (?, ?, ?)",
                (request_hash, json.dumps(request), json.dumps(response))
            )

    def get_cached_response(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached response for a request"""
        request_hash = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "SELECT response FROM cache WHERE request_hash = ?",
                (request_hash,)
            ).fetchone()
            return json.loads(result[0]) if result else None

# Initialize offline cache
offline_cache = OfflineCache()

def supports_color():
    """
    Returns True if the running system's terminal supports color,
    and False otherwise.
    """
    # If running in a known CI environment, assume no color support
    if os.environ.get('CI', False):
        return False

    # Check platform specific cases
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)

    # Check if we have an interactive terminal
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    # Check for Windows specific cases
    if plat == 'win32':
        try:
            from ctypes import windll
            return supported_platform and is_a_tty and windll.kernel32.GetConsoleMode(windll.kernel32.GetStdHandle(-11)) != 0
        except:
            return False

    # For all other platforms, check if we have a tty
    return supported_platform and is_a_tty

# ASCII Art for intro with ANSI colors
ASCII_INTRO = r"""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║       ____  _                 __  __            _     _                  ║
║      |  _ \(_)___  ___ ___   |  \/  | __ _  ___| |__ (_)_ __   __ _      ║
║      | | | | / __|/ __/ _ \  | |\/| |/ _` |/ __| '_ \| | '_ \ / _` |     ║
║      | |_| | \__ \ (_| (_) | | |  | | (_| | (__| | | | | | | | (_| |     ║
║      |____/|_|___/\___\___/  |_|  |_|\__,_|\___|_| |_|_|_| |_|\__,_|     ║
║                                                                          ║
║                                                                          ║
║                          AI-Powered Agent Suite                          ║
║                                                                          ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

              ⚪ Create ⚪ Analyze ⚪ Refactor ⚪ Test ⚪ Document

"""

# ASCII Art without colors as fallback
ASCII_INTRO_NO_COLOR = r"""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║       ____  _                 __  __            _     _                  ║
║      |  _ \(_)___  ___ ___   |  \/  | __ _  ___| |__ (_)_ __   __ _      ║
║      | | | | / __|/ __/ _ \  | |\/| |/ _` |/ __| '_ \| | '_ \ / _` |     ║
║      | |_| | \__ \ (_| (_) | | |  | | (_| | (__| | | | | | | | (_| |     ║
║      |____/|_|___/\___\___/  |_|  |_|\__,_|\___|_| |_|_|_| |_|\__,_|     ║
║                                                                          ║
║                                                                          ║
║                          AI-Powered Agent Suite                          ║
║                                                                          ║
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
    """Monitor job progress and stream output using WebSockets if available"""
    print_with_timestamp(f"Monitoring job {job_id}", "system")
    
    # Try to use WebSocket for real-time updates
    try:
        ws_url = f"ws://{server_url.split('://', 1)[1]}/ws/{job_id}"
        print_with_timestamp(f"Connecting to WebSocket for real-time updates...", "system")
        
        # Create message queue for threaded communication
        message_queue = queue.Queue()
        
        # Create WebSocket in a separate thread
        ws_thread = threading.Thread(
            target=run_websocket_client,
            args=(ws_url, message_queue, job_id),
            daemon=True
        )
        ws_thread.start()
        
        # Process WebSocket messages
        while True:
            try:
                # Non-blocking queue get with timeout
                try:
                    message = message_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Check for end marker
                if message == "__WEBSOCKET_CLOSED__":
                    print_with_timestamp("WebSocket connection closed", "system")
                    break
                    
                # Process normal message
                if isinstance(message, dict):
                    status = message.get("status")
                    progress = message.get("progress", 0)
                    msg_text = message.get("message", "")
                    
                    # Display appropriate message based on status
                    if status == "completed":
                        print_with_timestamp(f"Job completed successfully! 🎉", "success")
                        result = message.get("result", {})
                        
                        # Pretty print the result with colors if supported
                        format_and_print_json(result)
                        return
                    elif status == "failed":
                        print_with_timestamp("Job failed! ❌", "error")
                        error = message.get("error", "Unknown error")
                        print_with_timestamp(f"Error: {error}", "error")
                        return
                    else:
                        # Format progress bar
                        progress_str = format_progress_bar(progress)
                        print_with_timestamp(f"{msg_text} {progress_str}", "info")
                
            except Exception as e:
                print_with_timestamp(f"Error processing WebSocket message: {str(e)}", "error")
        
    except Exception as e:
        print_with_timestamp(f"WebSocket connection failed, falling back to polling: {str(e)}", "warning")
        
        # Fall back to traditional polling
        while True:
            try:
                response = requests.get(f"{server_url}/projects/{job_id}")
                if response.status_code == 200:
                    job_data = response.json()
                    status = job_data.get("status")
                    
                    if status == "completed":
                        print_with_timestamp(f"Job completed successfully! 🎉", "success")
                        result = job_data.get("result", {})
                        format_and_print_json(result)
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
                        progress = job_data.get("progress", 0)
                        progress_str = format_progress_bar(progress)
                        print_with_timestamp(f"Job status: {status} {indicator} {progress_str}", "info")
                else:
                    print_with_timestamp(f"Error checking job status: {response.status_code}", "error")
                    print_with_timestamp(response.text, "error")
                    break
            except Exception as e:
                print_with_timestamp(f"Error monitoring job: {str(e)}", "error")
                break
                
            time.sleep(interval)

def format_progress_bar(progress, width=20):
    """Format a text-based progress bar"""
    filled_width = int(width * progress / 100)
    bar = '█' * filled_width + '░' * (width - filled_width)
    
    if supports_color():
        return f"\033[38;5;76m[{bar}] {progress}%\033[0m"
    else:
        return f"[{bar}] {progress}%"

def format_and_print_json(data):
    """Format and print JSON with optional syntax highlighting"""
    if supports_color():
        formatted_json = json.dumps(data, indent=2)
        # Basic JSON syntax highlighting
        formatted_json = formatted_json.replace('{', '\033[38;5;208m{\033[0m')
        formatted_json = formatted_json.replace('}', '\033[38;5;208m}\033[0m')
        formatted_json = formatted_json.replace('[', '\033[38;5;208m[\033[0m')
        formatted_json = formatted_json.replace(']', '\033[38;5;208m]\033[0m')
        formatted_json = formatted_json.replace(':', '\033[38;5;208m:\033[0m')
        print(formatted_json)
    else:
        print(json.dumps(data, indent=2))

def run_websocket_client(ws_url, message_queue, job_id):
    """Run WebSocket client in a separate thread"""
    try:
        # Define callback functions
        def on_message(ws, message):
            try:
                data = json.loads(message)
                message_queue.put(data)
            except Exception as e:
                logger.error(f"WebSocket message parsing error: {str(e)}")
                message_queue.put({"status": "error", "error": str(e)})
                
        def on_error(ws, error):
            logger.error(f"WebSocket error: {str(error)}")
            message_queue.put({"status": "error", "error": str(error)})
            
        def on_close(ws, close_status_code, close_msg):
            logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
            message_queue.put("__WEBSOCKET_CLOSED__")
            
        def on_open(ws):
            logger.info(f"WebSocket connection established for job {job_id}")
            
        # Create and run WebSocket client
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        # Run WebSocket client with ping interval
        ws.run_forever(ping_interval=30)
        
    except Exception as e:
        logger.error(f"WebSocket thread error: {str(e)}")
        message_queue.put("__WEBSOCKET_CLOSED__")

def manually_compact():
    """Manually trigger context compaction"""
    if context_storage["messages"]:
        print_with_timestamp("Manually triggering context compaction...", "system")
        compact_context()
    else:
        print_with_timestamp("No context to compact yet.", "warning")

def resolve_workspace_path(provided_path=None):
    """
    Resolve and validate the workspace path.
    
    Args:
        provided_path (str, optional): Path provided by the user. Defaults to None.
        
    Returns:
        str: Absolute path to the workspace
        
    Raises:
        SystemExit: If the path is invalid or doesn't exist
    """
    # Use provided path or current working directory
    workspace_path = os.path.abspath(provided_path if provided_path else os.getcwd())
    
    # Validate path exists
    if not os.path.exists(workspace_path):
        print_with_timestamp(f"Error: Directory does not exist: {workspace_path}", "error")
        sys.exit(1)
    
    # Validate path is a directory
    if not os.path.isdir(workspace_path):
        print_with_timestamp(f"Error: Path is not a directory: {workspace_path}", "error")
        sys.exit(1)
        
    return workspace_path

def create_project(args):
    """Create a new project with enhanced CrewAI integration"""
    url = f"{args.server}/projects"
    
    # Resolve and validate workspace path
    codebase_dir = resolve_workspace_path(args.dir)
    
    # Enhanced request data with additional parameters for CrewAI
    data = {
        "project_goal": args.goal,
        "codebase_dir": codebase_dir,
        "non_interactive": not args.interactive,
        "process_type": args.process if hasattr(args, 'process') else "hierarchical",
        "model": args.model if hasattr(args, 'model') else None,
        "memory": args.memory if hasattr(args, 'memory') else True,
        "tools": args.tools if hasattr(args, 'tools') and args.tools else "all"
    }
    
    print_with_timestamp(f"Creating project with goal: {args.goal}", "info")
    print_with_timestamp(f"Using codebase directory: {codebase_dir}", "info")
    
    # Display enhanced settings
    interactive_mode = "🔄 Interactive" if args.interactive else "⏩ Non-interactive"
    print_with_timestamp(f"Mode: {interactive_mode}", "info")
    print_with_timestamp(f"Process Type: {data['process_type']}", "info")
    print_with_timestamp(f"Memory Enabled: {'Yes' if data['memory'] else 'No'}", "info")
    print_with_timestamp(f"Tools: {data['tools']}", "info")
    if data['model']:
        print_with_timestamp(f"Using Model: {data['model']}", "info")
    
    # Animate "Creating project" message with more detailed steps
    if supports_color():
        print("\033[38;5;205m", end="")
        print("Initializing Dev Team agents...", end="", flush=True)
        for _ in range(5):
            time.sleep(0.3)
            print(".", end="", flush=True)
        print("\033[0m")
        
        print("\033[38;5;39m", end="")
        print("Setting up agent hierarchy...", end="", flush=True)
        for _ in range(3):
            time.sleep(0.3)
            print(".", end="", flush=True)
        print("\033[0m")
        
        print("\033[38;5;76m", end="")
        print("Configuring tools and memory...", end="", flush=True)
        for _ in range(3):
            time.sleep(0.3)
            print(".", end="", flush=True)
        print("\033[0m")
    
    try:
        # Request with enhanced timeout for larger projects
        response = requests.post(url, json=data, timeout=60)
        if response.status_code == 201:
            job_data = response.json()
            job_id = job_data.get("job_id")
            print_with_timestamp(f"Project created with job ID: {job_id}", "success")
            
            # Store job ID in context storage for later use
            context_storage["current_job_id"] = job_id
            
            # Monitor the job progress with enhanced WebSocket support
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
    """Replay a specific task with enhanced CrewAI features"""
    url = f"{args.server}/tasks/replay"
    
    # Enhanced data with CrewAI settings
    data = {
        "task_index": args.index,
        "process_type": args.process if hasattr(args, 'process') else "hierarchical",
        "model": args.model if hasattr(args, 'model') else None,
        "memory": args.memory if hasattr(args, 'memory') else True,
        "tools": args.tools if hasattr(args, 'tools') and args.tools else "all",
        "verbose": args.verbose if hasattr(args, 'verbose') else True,
        "with_delegation": args.delegation if hasattr(args, 'delegation') else True
    }
    
    print_with_timestamp(f"Replaying task with index: {args.index}", "info")
    print_with_timestamp(f"Process Type: {data['process_type']}", "info")
    print_with_timestamp(f"Memory Enabled: {'Yes' if data['memory'] else 'No'}", "info")
    print_with_timestamp(f"Agent Delegation: {'Enabled' if data['with_delegation'] else 'Disabled'}", "info")
    if data['model']:
        print_with_timestamp(f"Using Model: {data['model']}", "info")
    
    # Animate "Replaying task" message with detailed steps
    if supports_color():
        print("\033[38;5;205m", end="")
        print("Initializing replay environment...", end="", flush=True)
        for _ in range(3):
            time.sleep(0.3)
            print(".", end="", flush=True)
        print("\033[0m")
        
        print("\033[38;5;76m", end="")
        print("Loading task context and dependencies...", end="", flush=True)
        for _ in range(3):
            time.sleep(0.3)
            print(".", end="", flush=True)
        print("\033[0m")
    
    try:
        # Request with enhanced timeout for complex tasks
        response = requests.post(url, json=data, timeout=60)
        if response.status_code == 202:
            job_data = response.json()
            job_id = job_data.get("job_id")
            print_with_timestamp(f"Task replay queued with job ID: {job_id}", "success")
            
            # Store job ID in context storage for later use
            context_storage["current_job_id"] = job_id
            
            # Monitor the job progress with enhanced WebSocket support
            monitor_job(job_id, args.server)
        else:
            print_with_timestamp(f"Error replaying task: {response.status_code}", "error")
            print_with_timestamp(response.text, "error")
    except Exception as e:
        print_with_timestamp(f"Error: {str(e)}", "error")

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
        
def get_workspace_info():
    """Get information about the current workspace directory"""
    workspace_path = os.getcwd()
    workspace_info = {
        "path": workspace_path,
        "name": os.path.basename(workspace_path),
        "files": [],
        "directories": [],
        "config_files": []
    }
    
    # Common configuration files to look for
    config_files = [
        "package.json", "requirements.txt", "pyproject.toml", "setup.py",
        "docker-compose.yml", "Dockerfile", ".env", "README.md",
        "tsconfig.json", "next.config.js", "tailwind.config.js"
    ]
    
    try:
        for root, dirs, files in os.walk(workspace_path):
            # Skip hidden directories and common build/cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '.next', '__pycache__']]
            
            rel_path = os.path.relpath(root, workspace_path)
            if rel_path == '.':
                workspace_info["directories"] = dirs
                for file in files:
                    if file in config_files:
                        workspace_info["config_files"].append(file)
                    else:
                        workspace_info["files"].append(file)
    except Exception as e:
        logger.error(f"Error scanning workspace: {e}")
    
    return workspace_info

def initialize_chat_history(codebase_dir: str) -> List[Dict[str, str]]:
    """Initialize chat history with system message and workspace context"""
    workspace_info = get_workspace_info()
    
    workspace_context = f"""
Current workspace: {workspace_info['path']}
Project name: {workspace_info['name']}
Configuration files: {', '.join(workspace_info['config_files'])}
Main directories: {', '.join(workspace_info['directories'])}
Key files: {', '.join(workspace_info['files'][:10])}{'...' if len(workspace_info['files']) > 10 else ''}
"""
    
    return [{
        "role": "system",
        "content": f"You are the Project Manager agent for a software development team. "
                  f"You're working with a codebase located at {workspace_info['path']}. "
                  f"Here is the workspace context:\n{workspace_context}\n"
                  f"Provide helpful, concise responses to the user's questions about their project."
    }]

def chat_with_agent(args):
    """Start an interactive chat with the Project Manager agent with improved features"""
    url = f"{args.server}/chat"
    
    # Get workspace information
    workspace_info = get_workspace_info()
    print_with_timestamp(f"Analyzing workspace: {workspace_info['path']}", "system")
    
    # Setup command history
    history_file = os.path.join(os.path.expanduser("~"), ".discomachina", "chat_history")
    try:
        readline.read_history_file(history_file)
    except FileNotFoundError:
        pass
    atexit.register(readline.write_history_file, history_file)
    
    # Welcome message with workspace context
    display_welcome_message()
    if supports_color():
        print(f"\033[38;5;39mWorkspace:\033[0m \033[38;5;76m{workspace_info['path']}\033[0m")
        print(f"\033[38;5;39mProject:\033[0m \033[38;5;76m{workspace_info['name']}\033[0m")
    else:
        print(f"Workspace: {workspace_info['path']}")
        print(f"Project: {workspace_info['name']}")
    
    # Initialize chat history with workspace context
    chat_history = initialize_chat_history(workspace_info['path'])
    
    # Check server connectivity and set up offline mode if needed
    setup_server_connection(args)
    
    # Main chat loop with improved features
    while True:
        try:
            # Get user input with proper command completion
            user_input = get_user_input()
            
            if should_exit(user_input):
                display_goodbye_message()
                break
            
            # Handle special commands
            if handle_special_command(user_input):
                continue
            
            # Process user input and get response
            response = process_chat_message(user_input, chat_history, args, workspace_info['path'])
            
            # Display response with proper formatting
            display_agent_response(response)
            
            # Update chat history and manage context
            update_chat_history(chat_history, user_input, response)
            
        except KeyboardInterrupt:
            print("\nChat interrupted. Use 'exit' to quit properly.")
            continue
        except Exception as e:
            handle_chat_error(e)

def setup_server_connection(args):
    """Check server connectivity and set up offline mode if needed"""
    try:
        if not check_server_status(args.server):
            logger.warning(f"Unable to connect to server at {args.server}")
            context_storage["offline_mode"] = True
            print_with_timestamp("Entering offline mode. Some features may be limited.", "warning")
        else:
            context_storage["offline_mode"] = False
            print_with_timestamp("Connected to server! 🚀", "success")
    except Exception as e:
        logger.error(f"Error checking server status: {e}")
        context_storage["offline_mode"] = True
        print_with_timestamp("Entering offline mode due to connection error.", "warning")

def process_chat_message(user_input: str, chat_history: List[Dict[str, str]], args, current_dir: str) -> str:
    """Process chat message and get response"""
    if context_storage["offline_mode"]:
        # Try to get response from cache in offline mode
        cached_response = offline_cache.get_cached_response({"input": user_input})
        if cached_response:
            return cached_response["response"]
        return "I'm currently in offline mode and don't have a cached response for this query."
    
    try:
        # Get current workspace info
        workspace_info = get_workspace_info()
        
        # Add workspace context to the request
        request_data = {
            "messages": chat_history + [{"role": "user", "content": user_input}],
            "model": args.model if args.model else "default",
            "workspace_context": {
                "path": workspace_info["path"],
                "name": workspace_info["name"],
                "config_files": workspace_info["config_files"],
                "directories": workspace_info["directories"],
                "files": workspace_info["files"]
            },
            "current_dir": current_dir
        }
        
        response = send_chat_request(request_data, args)
        # Cache successful response for offline mode
        offline_cache.cache_response(
            {"input": user_input},
            {"response": response}
        )
        return response
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return f"I encountered an error: {str(e)}"

def send_chat_request(request_data: Dict[str, Any], args) -> str:
    """Send chat request to server"""
    url = f"{args.server}/chat"
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=request_data, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Server error: {response.status_code}")

def update_chat_history(chat_history: List[Dict[str, str]], user_input: str, response: str):
    """Update chat history and manage context"""
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": response})
    
    # Check if we need to compact history
    if len(chat_history) > 20:  # Arbitrary threshold
        compact_chat_history(chat_history)

def compact_chat_history(chat_history: List[Dict[str, str]]):
    """Compact chat history while preserving context"""
    system_message = chat_history[0]
    recent_messages = chat_history[-10:]  # Keep last 5 exchanges
    summary = create_history_summary(chat_history[1:-10])
    
    chat_history.clear()
    chat_history.append(system_message)
    chat_history.append({"role": "system", "content": f"Previous conversation summary: {summary}"})
    chat_history.extend(recent_messages)

def create_history_summary(messages: List[Dict[str, str]]) -> str:
    """Create a summary of chat history"""
    # In a real implementation, you might want to use an AI model to create this summary
    return f"[{len(messages)} previous messages summarized]"

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
        if supports_color():
            print(f"\033[38;5;226mDisco-Machina\033[0m \033[38;5;245mversion\033[0m \033[38;5;76m{__version__}\033[0m")
        else:
            print(f"Disco-Machina version {__version__}")
    except:
        print("Disco-Machina version unknown")

def display_welcome_message():
    """Display welcome message with proper formatting"""
    header = "Project Manager Agent Chat"
    box_width = 70
    padding = (box_width - len(header) - 2) // 2
    
    if supports_color():
        print("\n\033[38;5;51m╔" + "═" * box_width + "╗\033[0m")
        print(f"\033[38;5;51m║\033[0m{' ' * padding}{header}{' ' * (box_width - len(header) - padding - 2)}\033[38;5;51m║\033[0m")
        print("\033[38;5;51m╚" + "═" * box_width + "╝\033[0m\n")
    else:
        print("\n╔" + "═" * box_width + "╗")
        print(f"║{' ' * padding}{header}{' ' * (box_width - len(header) - padding - 2)}║")
        print("╚" + "═" * box_width + "╝\n")
    
    print_with_timestamp("Starting chat session with Project Manager agent...", "system")

def get_user_input() -> str:
    """Get user input with command completion"""
    if supports_color():
        prompt = "\n\033[38;5;39m[You]\033[0m "
    else:
        prompt = "\n[You] "
    
    try:
        return input(prompt)
    except EOFError:
        raise KeyboardInterrupt

def should_exit(user_input: str) -> bool:
    """Check if user wants to exit"""
    return user_input.lower() in ["exit", "quit", "bye", "goodbye"]

def display_goodbye_message():
    """Display goodbye message"""
    print_with_timestamp("\nEnding chat session. Goodbye! 👋", "success")

def handle_special_command(user_input: str) -> bool:
    """Handle special commands"""
    special_commands = {
        "/help": display_help,
        "/clear": clear_screen,
        "/status": display_status,
        "/compact": manually_compact,
        "/version": print_version
    }
    
    command = user_input.split()[0] if user_input.split() else ""
    if command in special_commands:
        special_commands[command]()
        return True
    return False

def display_help():
    """Display help information"""
    help_text = """
Available Commands:
-----------------
/help     - Show this help message
/clear    - Clear the screen
/status   - Show server and session status
/compact  - Manually compact chat history
/version  - Show version information
exit      - End the chat session
"""
    if supports_color():
        print("\033[38;5;226m" + help_text + "\033[0m")
    else:
        print(help_text)

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_status():
    """Display server and session status"""
    status = {
        "Server Mode": "Offline" if context_storage["offline_mode"] else "Online",
        "Session ID": context_storage["session_id"] or "Not established",
        "Messages in Context": len(context_storage["messages"]),
        "Token Count": context_storage["token_count"],
        "Max Tokens": context_storage["max_tokens"]
    }
    
    if supports_color():
        print("\n\033[38;5;93mCurrent Status:\033[0m")
        for key, value in status.items():
            print(f"\033[38;5;245m{key}:\033[0m \033[38;5;76m{value}\033[0m")
    else:
        print("\nCurrent Status:")
        for key, value in status.items():
            print(f"{key}: {value}")

def display_agent_response(response: str):
    """Display agent response with proper formatting"""
    if supports_color():
        print("\n\033[38;5;76m[Project Manager]\033[0m " + response + "\n")
    else:
        print("\n[Project Manager] " + response + "\n")

def handle_chat_error(error: Exception):
    """Handle chat errors gracefully"""
    logger.error(f"Chat error: {str(error)}")
    
    if isinstance(error, requests.exceptions.Timeout):
        print_with_timestamp("Request timed out. The server is taking too long to respond.", "error")
    elif isinstance(error, requests.exceptions.ConnectionError):
        print_with_timestamp("Connection error. The server might be down or unreachable.", "error")
        print_with_timestamp("Switching to offline mode...", "warning")
        context_storage["offline_mode"] = True
    else:
        print_with_timestamp(f"Error: {str(error)}", "error")
    
    print_with_timestamp("Would you like to:", "system")
    print_with_timestamp("1. Retry", "info")
    print_with_timestamp("2. Start a new chat", "info")
    print_with_timestamp("3. Switch to offline mode", "info")
    print_with_timestamp("4. Exit", "info")
    
    try:
        choice = input("Enter your choice (1-4): ")
        handle_error_choice(choice)
    except (KeyboardInterrupt, EOFError):
        print("\nExiting due to interrupt...")
        sys.exit(1)

def handle_error_choice(choice: str):
    """Handle user's choice after an error"""
    if choice == "1":
        return  # Will retry in the main loop
    elif choice == "2":
        context_storage["messages"].clear()
        print_with_timestamp("Starting a new chat session...", "system")
    elif choice == "3":
        context_storage["offline_mode"] = True
        print_with_timestamp("Switched to offline mode. Some features may be limited.", "warning")
    else:
        print_with_timestamp("Ending chat session due to error.", "error")
        sys.exit(1)

def train_crew(args):
    """Train a crew with enhanced CrewAI integration"""
    url = f"{args.server}/train"
    
    # Resolve and validate workspace path
    codebase_dir = resolve_workspace_path(args.dir)
    
    # Enhanced request data with training parameters
    data = {
        "project_goal": args.goal,
        "codebase_dir": codebase_dir,
        "iterations": args.iterations,
        "output_file": args.output,
        "process_type": args.process if hasattr(args, 'process') else "hierarchical",
        "model": args.model if hasattr(args, 'model') else None,
        "memory": args.memory if hasattr(args, 'memory') else True,
        "tools": args.tools if hasattr(args, 'tools') and args.tools else "all"
    }
    
    print_with_timestamp(f"Training crew on goal: {args.goal}", "info")
    print_with_timestamp(f"Using codebase directory: {codebase_dir}", "info")
    print_with_timestamp(f"Training iterations: {args.iterations}", "info")
    print_with_timestamp(f"Output file: {args.output}", "info")
    
    # Display enhanced settings
    print_with_timestamp(f"Process Type: {data['process_type']}", "info")
    print_with_timestamp(f"Memory Enabled: {'Yes' if data['memory'] else 'No'}", "info")
    print_with_timestamp(f"Tools: {data['tools']}", "info")
    if data['model']:
        print_with_timestamp(f"Using Model: {data['model']}", "info")
    
    # Animate "Training crew" message
    if supports_color():
        print("\033[38;5;205m", end="")
        print("Initializing training session...", end="", flush=True)
        for _ in range(5):
            time.sleep(0.3)
            print(".", end="", flush=True)
        print("\033[0m")
    
    try:
        # Request with enhanced timeout for training sessions
        response = requests.post(url, json=data, timeout=60)
        if response.status_code == 202:
            job_data = response.json()
            job_id = job_data.get("job_id")
            print_with_timestamp(f"Training session queued with job ID: {job_id}", "success")
            
            # Store job ID in context storage for later use
            context_storage["current_job_id"] = job_id
            
            # Monitor the job progress with enhanced WebSocket support
            monitor_job(job_id, args.server)
        else:
            print_with_timestamp(f"Error starting training session: {response.status_code}", "error")
            print_with_timestamp(response.text, "error")
    except Exception as e:
        print_with_timestamp(f"Error: {str(e)}", "error")

def test_crew(args):
    """Test a crew with various models and configurations"""
    url = f"{args.server}/test"
    
    # Resolve and validate workspace path
    codebase_dir = resolve_workspace_path(args.dir)
    
    # Enhanced request data with testing parameters
    data = {
        "project_goal": args.goal,
        "codebase_dir": codebase_dir,
        "iterations": args.iterations,
        "model": args.model,
        "process_type": args.process if hasattr(args, 'process') else "hierarchical",
        "memory": args.memory if hasattr(args, 'memory') else True,
        "tools": args.tools if hasattr(args, 'tools') and args.tools else "all"
    }
    
    print_with_timestamp(f"Testing crew on goal: {args.goal}", "info")
    print_with_timestamp(f"Using codebase directory: {codebase_dir}", "info")
    print_with_timestamp(f"Test iterations: {args.iterations}", "info")
    print_with_timestamp(f"Testing model: {args.model}", "info")
    
    # Display enhanced settings
    print_with_timestamp(f"Process Type: {data['process_type']}", "info")
    print_with_timestamp(f"Memory Enabled: {'Yes' if data['memory'] else 'No'}", "info")
    print_with_timestamp(f"Tools: {data['tools']}", "info")
    
    # Animate "Testing crew" message
    if supports_color():
        print("\033[38;5;205m", end="")
        print("Initializing test session...", end="", flush=True)
        for _ in range(5):
            time.sleep(0.3)
            print(".", end="", flush=True)
        print("\033[0m")
    
    try:
        # Request with enhanced timeout for test sessions
        response = requests.post(url, json=data, timeout=60)
        if response.status_code == 202:
            job_data = response.json()
            job_id = job_data.get("job_id")
            print_with_timestamp(f"Test session queued with job ID: {job_id}", "success")
            
            # Store job ID in context storage for later use
            context_storage["current_job_id"] = job_id
            
            # Monitor the job progress with enhanced WebSocket support
            monitor_job(job_id, args.server)
        else:
            print_with_timestamp(f"Error starting test session: {response.status_code}", "error")
            print_with_timestamp(response.text, "error")
    except Exception as e:
        print_with_timestamp(f"Error: {str(e)}", "error")

def main():
    # Create main parser
    parser = argparse.ArgumentParser(description="Disco-Machina - Terminal client")
    parser.add_argument("--server", default="http://localhost:8000", help="Server URL")
    parser.add_argument("--version", action="store_true", help="Show version information")
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create parser for "create" command with enhanced CrewAI options
    create_parser = subparsers.add_parser("create", help="Create a new project with CrewAI agents")
    create_parser.add_argument("--goal", required=True, help="Project goal")
    create_parser.add_argument("--dir", help="Codebase directory (defaults to current directory)")
    create_parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    create_parser.add_argument("--process", choices=["sequential", "parallel", "hierarchical"], 
                             default="hierarchical", help="CrewAI process type (default: hierarchical)")
    create_parser.add_argument("--model", help="LLM model to use (e.g., gpt-4, gpt-3.5-turbo, claude-3-opus)")
    create_parser.add_argument("--memory", action="store_true", default=True, 
                             help="Enable agent memory for better context retention (default: True)")
    create_parser.add_argument("--no-memory", action="store_false", dest="memory", 
                             help="Disable agent memory")
    create_parser.add_argument("--tools", help="Comma-separated list of tools to enable, or 'all' for all tools")
    create_parser.add_argument("--delegation", action="store_true", default=True,
                             help="Enable agent delegation (default: True)")
    create_parser.add_argument("--no-delegation", action="store_false", dest="delegation",
                             help="Disable agent delegation")
    create_parser.set_defaults(func=create_project)
    
    # Create parser for "train" command with enhanced CrewAI options
    train_parser = subparsers.add_parser("train", help="Train a crew with multiple iterations")
    train_parser.add_argument("iterations", type=int, help="Number of training iterations")
    train_parser.add_argument("output", help="Output file for training results")
    train_parser.add_argument("--goal", required=True, help="Project goal for training")
    train_parser.add_argument("--dir", help="Codebase directory (defaults to current directory)")
    train_parser.add_argument("--process", choices=["sequential", "parallel", "hierarchical"], 
                             default="hierarchical", help="CrewAI process type (default: hierarchical)")
    train_parser.add_argument("--model", help="LLM model to use (e.g., gpt-4, gpt-3.5-turbo, claude-3-opus)")
    train_parser.add_argument("--memory", action="store_true", default=True, 
                             help="Enable agent memory for better context retention (default: True)")
    train_parser.add_argument("--no-memory", action="store_false", dest="memory", 
                             help="Disable agent memory")
    train_parser.add_argument("--tools", help="Comma-separated list of tools to enable, or 'all' for all tools")
    train_parser.set_defaults(func=train_crew)
    
    # Create parser for "test" command with enhanced CrewAI options
    test_parser = subparsers.add_parser("test", help="Test a crew with a specific model")
    test_parser.add_argument("iterations", type=int, help="Number of test iterations")
    test_parser.add_argument("model", help="LLM model to test with")
    test_parser.add_argument("--goal", required=True, help="Project goal for testing")
    test_parser.add_argument("--dir", help="Codebase directory (defaults to current directory)")
    test_parser.add_argument("--process", choices=["sequential", "parallel", "hierarchical"], 
                            default="hierarchical", help="CrewAI process type (default: hierarchical)")
    test_parser.add_argument("--memory", action="store_true", default=True, 
                            help="Enable agent memory for better context retention (default: True)")
    test_parser.add_argument("--no-memory", action="store_false", dest="memory", 
                            help="Disable agent memory")
    test_parser.add_argument("--tools", help="Comma-separated list of tools to enable, or 'all' for all tools")
    test_parser.set_defaults(func=test_crew)
    
    # Create parser for "list" command
    list_parser = subparsers.add_parser("list", help="List all projects")
    list_parser.set_defaults(func=list_projects)
    
    # Create parser for "get" command
    get_parser = subparsers.add_parser("get", help="Get project status")
    get_parser.add_argument("job_id", help="Job ID")
    get_parser.set_defaults(func=get_project)
    
    # Create parser for "replay" command with enhanced CrewAI options
    replay_parser = subparsers.add_parser("replay", help="Replay a task with CrewAI agents")
    replay_parser.add_argument("index", type=int, help="Task index")
    replay_parser.add_argument("--process", choices=["sequential", "parallel", "hierarchical"], 
                             default="hierarchical", help="CrewAI process type (default: hierarchical)")
    replay_parser.add_argument("--model", help="LLM model to use (e.g., gpt-4, gpt-3.5-turbo, claude-3-opus)")
    replay_parser.add_argument("--memory", action="store_true", default=True, 
                             help="Enable agent memory for better context retention (default: True)")
    replay_parser.add_argument("--no-memory", action="store_false", dest="memory", 
                             help="Disable agent memory")
    replay_parser.add_argument("--tools", help="Comma-separated list of tools to enable, or 'all' for all tools")
    replay_parser.add_argument("--verbose", action="store_true", default=True,
                             help="Enable verbose output (default: True)")
    replay_parser.add_argument("--quiet", action="store_false", dest="verbose",
                             help="Disable verbose output")
    replay_parser.add_argument("--delegation", action="store_true", default=True,
                             help="Enable agent delegation (default: True)")
    replay_parser.add_argument("--no-delegation", action="store_false", dest="delegation",
                             help="Disable agent delegation")
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
    chat_parser.add_argument("--dir", help="Target codebase directory (defaults to current directory)")
    chat_parser.add_argument("--memory", action="store_true", default=True, 
                          help="Enable agent memory for better context retention (default: True)")
    chat_parser.add_argument("--no-memory", action="store_false", dest="memory", 
                          help="Disable agent memory")
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
            print_with_timestamp("Make sure the Disco-Machina API server is running.", "warning")
            
            if supports_color():
                response = input("\033[38;5;208mDo you want to continue anyway? (y/n): \033[0m")
            else:
                response = input("Do you want to continue anyway? (y/n): ")
                
            if response.lower() != 'y':
                return
        else:
            print_with_timestamp("Connected to Disco-Machina API server! 🚀", "success")
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