# Disco-Machina

AI-powered software development terminal client with chat and API server integration.

## Overview

Disco-Machina is a self-contained terminal client that provides intelligent codebase analysis and development assistance. It automatically detects and analyzes your current workspace, providing context-aware responses and insights about your codebase.

## Key Features

- **Interactive Terminal Client**
  - Beautiful ASCII art interface with color support
  - Command history and completion
  - Special commands for enhanced functionality
  - Real-time status updates

- **Automatic Workspace Detection**
  - Automatically detects current working directory
  - Scans project structure and configuration files
  - Identifies key dependencies and technologies
  - Provides context-aware responses

- **RAG-Based Analysis**
  - Retrieval Augmented Generation for accurate codebase understanding
  - Real-time workspace context in every interaction
  - Intelligent file and directory analysis
  - Configuration file detection and parsing

- **Offline Mode Support**
  - Graceful degradation when server is unavailable
  - Local caching of responses
  - Automatic context management
  - Persistent chat history

- **Context Management**
  - Smart context compaction
  - Token-aware message handling
  - Automatic history summarization
  - Workspace-aware responses

- **Error Handling & Recovery**
  - Graceful error handling
  - Automatic retry mechanisms
  - Offline mode fallback
  - Clear error reporting

- **User Experience**
  - Color-coded output
  - Progress indicators
  - Keyboard shortcuts
  - Clear status messages

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yavuztopsever/disco-machina.git
cd disco-machina
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
BRAVE_API_KEY=your_brave_api_key  # Optional
GH_TOKEN=your_github_token  # Optional
```

## Usage

### Basic Commands

1. Start a chat session:
```bash
discomachina chat
```

2. Create a new project:
```bash
discomachina create --goal "Analyze this codebase" --interactive
```

3. List all projects:
```bash
discomachina list
```

4. Get project status:
```bash
discomachina get <job_id>
```

5. Replay a task:
```bash
discomachina replay <index>
```

### Chat Commands

While in chat mode, you can use these special commands:
- `/help` - Show available commands
- `/clear` - Clear the screen
- `/status` - Show server and session status
- `/compact` - Manually compact chat history
- `/version` - Show version information
- `exit` - End the chat session

### Workspace Analysis

The client automatically:
1. Detects your current working directory
2. Scans for configuration files and project structure
3. Identifies key dependencies and technologies
4. Provides context-aware responses about your codebase

### Docker Support

1. Using docker-compose:
```bash
docker-compose up -d
```

2. Running the Docker image directly:
```bash
docker run -p 8000:8000 disco-machina:latest
```

## Project Structure

```
disco-machina/
├── terminal_client.py    # Main terminal client application
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile          # Docker build configuration
└── .env               # Environment variables (create this)
```

## Features

### Automatic Workspace Detection
- Detects current working directory
- Scans project structure
- Identifies configuration files
- Provides real-time context

### RAG-Based Analysis
- Intelligent codebase understanding
- Context-aware responses
- Real-time workspace updates
- Configuration file parsing

### Offline Mode
- Local caching of responses
- Graceful degradation
- Persistent chat history
- Automatic context management

### Error Handling
- Graceful error recovery
- Clear error messages
- Automatic retry
- Offline fallback

### User Experience
- Color-coded output
- Progress indicators
- Keyboard shortcuts
- Status messages

## Author

Created by Yavuz Topsever (https://github.com/yavuztopsever)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
