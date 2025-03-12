# Disco-Machina Terminal Client
Created by Yavuz Topsever (https://github.com/yavuztopsever)

## Overview

Disco-Machina is a terminal client for interacting with the Dev Team API server. It provides a user-friendly interface for creating projects, tracking progress, and chatting with the AI-powered Project Manager agent.

## Core Features

1. **Project Creation**: Create new development projects with specific goals
2. **Project Tracking**: List and monitor the status of ongoing projects 
3. **Task Replay**: Replay specific tasks from previous runs
4. **Memory Management**: Reset agent memories when needed
5. **Interactive Chat**: Communicate directly with the Project Manager agent

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd dev_team

# Install dependencies
pip install -r requirements.txt

# Make sure the server is running
python -m src.dev_team.server
```

## Usage

### Basic Commands

```bash
# Create a new project
python terminal_client.py create --goal "Create a REST API for a blog" --interactive

# List all projects
python terminal_client.py list

# Get details for a specific project
python terminal_client.py get <job-id>

# Replay a specific task
python terminal_client.py replay <task-index>

# Reset agent memories
python terminal_client.py reset [--type all|short|long]

# Chat with the Project Manager agent
python terminal_client.py chat [--model model-name]
```

### Chat with Project Manager Agent

The chat feature allows you to communicate directly with the Project Manager agent. This enables you to:

- Ask questions about your codebase
- Get recommendations for architecture and design
- Brainstorm new features
- Analyze existing code
- Plan development sprints
- Request technical research

To start a chat session:

```bash
python terminal_client.py chat
```

During the chat, you can:
- Type your questions or commands directly
- Type "exit" or "quit" to end the session
- Press Ctrl+Z to manually compact the context window
- Press Ctrl+C to exit immediately

### Troubleshooting

If you encounter issues with the terminal client, you can try:

1. **Connection Issues**:
   - Make sure the server is running (`python -m src.dev_team.server`)
   - Check server logs for any error messages
   - Verify the server URL (default: http://localhost:8000)

2. **Chat Issues**:
   - If the chat terminal interface doesn't work, try the alternative chat clients:
     - `python simple_chat.py` - A simplified chat interface
     - `python robust_chat.py` - Works in both interactive and non-interactive environments

3. **Input/Output Issues**:
   - If you encounter EOFError or similar issues, it might be related to your terminal environment
   - Try using the robust_chat.py script which handles these cases

## Advanced Usage

### Custom Server URL

```bash
python terminal_client.py --server http://custom-server:port chat
```

### Specifying a Model

```bash
python terminal_client.py chat --model "gpt-4"
```

### Creating Non-Interactive Projects

```bash
python terminal_client.py create --goal "Analyze this codebase" --dir "/path/to/codebase"
```

## Development

The terminal client is designed to be extensible. Key files:

- `terminal_client.py`: Main client implementation
- `simple_chat.py`: Simplified chat client
- `robust_chat.py`: Chat client that works in all environments
- `test_chat.py`: Test script for the chat functionality

To add new commands, extend the argument parser in the `main()` function.