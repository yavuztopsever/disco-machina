# DiscoMachina

AI-powered software development terminal client with chat and API server integration.

## Overview

DiscoMachina is a self-contained terminal client that provides intelligent codebase analysis and development assistance. It implements a hierarchical team structure with specialized AI agents working together to handle various aspects of software development.

## System Architecture

### Core Components

1. **Terminal Client**
   - Interactive command-line interface
   - Real-time output and status updates
   - Command history and completion
   - Color-coded output and progress indicators

2. **API Server**
   - FastAPI-based REST API
   - Background task processing
   - Job management and status tracking
   - WebSocket support for real-time updates

3. **Development Team**
   - Project Manager: Requirements analysis and team coordination
   - Software Architect: System design and code structure
   - Fullstack Developer: Feature implementation
   - Test Engineer: Quality assurance and testing

4. **Development Tools**
   - Requirements Analysis
   - Task Tracking
   - Code Analysis
   - Test Generation
   - And more...

### Key Features

- **Interactive Terminal Client**
  - Beautiful ASCII art interface with color support
  - Command history and completion
  - Special commands for enhanced functionality
  - Real-time status updates

- **Real-time Updates with WebSockets**
  - Live progress updates via WebSocket connections
  - Interactive progress bars with percentage indicators
  - Fallback to polling when WebSockets unavailable
  - Instant notification of job completion or failure

- **Automatic Workspace Detection**
  - Automatically detects current working directory
  - Scans project structure and configuration files
  - Identifies key dependencies and technologies
  - Provides context-aware responses

- **Enhanced Error Recovery**
  - Exponential backoff for failed tasks
  - Smart retry mechanism with configurable attempts
  - Critical path analysis for error handling
  - Detailed error reporting and logging

- **Task Checkpointing**
  - Automatic checkpoints after each task
  - Resume capability after interruption
  - Backup of checkpoint data for safety
  - Skip completed tasks on restart

- **RAG-Based Analysis**
  - Retrieval Augmented Generation for accurate codebase understanding
  - Real-time workspace context in every interaction
  - Intelligent file and directory analysis
  - Configuration file detection and parsing

- **Improved Offline Mode**
  - Enhanced graceful degradation when server is unavailable
  - Sophisticated local caching of responses
  - Automatic context management
  - Persistent chat history with SQLite storage

- **Advanced Context Management**
  - Smart context compaction with token tracking
  - Intelligent message summarization
  - Automatic history pruning with context preservation
  - Workspace-aware responses with state persistence

- **User Experience**
  - Color-coded output with theme support
  - Interactive progress indicators
  - Keyboard shortcuts for power users
  - Clear, concise status messages

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

### Main Flow - Working Directory Based Operation

1. Navigate to your project directory:
```bash
cd /path/to/your/project
```

2. Launch DiscoMachina in chat mode:
```bash
discomachina chat
```

That's it! DiscoMachina automatically:
- Uses your current directory as the working context
- Analyzes your codebase structure, files, and configuration
- Provides AI assistance specific to your project
- Contains all operations within your project directory

### Basic Commands

1. **Start a chat session with your current codebase:**
```bash
# Navigate to your project first
cd /path/to/your/project

# Start a chat session
discomachina chat

# With specific options
discomachina chat --model "claude-3-opus" --memory
```

2. **Create a new project with CrewAI options:**
```bash
discomachina create --goal "Analyze this codebase" \
  --process hierarchical \
  --memory \
  --delegation \
  --tools "CodeAnalysisTool,CodebaseAnalysisTool,BraveSearchTool"
```

3. **Train the crew with iterations:**
```bash
discomachina train 3 results.json \
  --goal "Optimize React components" \
  --model "gpt-4" \
  --process hierarchical
```

4. **Test with different models:**
```bash
discomachina test 2 "claude-3-opus" \
  --goal "Refactor Python code" \
  --process hierarchical
```

5. **Replay a specific task:**
```bash
discomachina replay 2 \
  --process hierarchical \
  --memory \
  --delegation \
  --verbose
```

6. **Other utility commands:**
```bash
# List all projects
discomachina list

# Get project status
discomachina get <job_id>

# Reset agent memory
discomachina reset --type all

# Manually compact context
discomachina compact
```

### Chat Commands

While in chat mode, you can use these special commands:
- `/help` - Show available commands
- `/clear` - Clear the screen
- `/status` - Show server and session status
- `/compact` - Manually compact chat history
- `/version` - Show version information
- `exit` - End the chat session

### CrewAI Process Types

DiscoMachina supports all CrewAI process types:

- **Hierarchical** (default): Agents work in a hierarchy with delegation
- **Sequential**: Agents work in sequence, one after another
- **Parallel**: Agents work in parallel on independent tasks

Example:
```bash
discomachina create --goal "Refactor code" --process parallel
```

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
├── src/
│   └── dev_team/
│       ├── main.py      # Main entry point
│       ├── crew.py      # Dev Team implementation
│       ├── server.py    # API server
│       ├── tools/       # Development tools
│       └── config/      # Configuration files
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile          # Docker build configuration
└── .env               # Environment variables (create this)
```

## Development Team

### Project Manager
- Role: Project coordination and requirements analysis
- Tools: Requirements Analysis, Task Tracking, Agile Project Management
- Responsibilities:
  - Analyze project requirements
  - Create sprint plans
  - Coordinate team activities
  - Ensure project success

### Software Architect
- Role: System design and code structure
- Tools: Code Analysis, Codebase Analysis, Code Refactoring
- Responsibilities:
  - Design system architecture
  - Analyze code structure
  - Recommend improvements
  - Ensure maintainable code

### Fullstack Developer
- Role: Feature implementation
- Tools: Code Implementation, Code Generation, Dependency Management
- Responsibilities:
  - Implement features
  - Fix bugs
  - Manage dependencies
  - Ensure code quality

### Test Engineer
- Role: Quality assurance and testing
- Tools: Test Generation, Test Runner, Code Coverage
- Responsibilities:
  - Create tests
  - Ensure code coverage
  - Perform code reviews
  - Maintain code quality

## Development Tools

### Requirements & Planning
- Requirements Analysis Tool
- Task Tracking Tool
- Agile Project Management Tool

### Code Analysis & Design
- Code Analysis Tool
- Codebase Analysis Tool
- Code Refactoring Tool
- Obsolete Code Cleanup Tool

### Implementation
- Code Implementation Tool
- Code Generation Tool
- Dependency Management Tool

### Testing & Quality
- Test Generation Tool
- Test Runner Tool
- Code Coverage Tool
- Code Review Tool

## API Endpoints

### Projects
- `POST /projects` - Create a new project with CrewAI options (process_type, memory, tools, delegation)
- `GET /projects` - List all projects
- `GET /projects/{job_id}` - Get project status

### Tasks
- `POST /tasks/replay` - Replay a specific task with CrewAI options

### Training & Testing
- `POST /train` - Train a crew with multiple iterations
- `POST /test` - Test a crew with a specific model

### Memory
- `POST /memory/reset` - Reset agent memory

### Chat
- `POST /chat` - Chat with the Project Manager agent with memory options

### WebSockets
- `WebSocket /ws/{job_id}` - Real-time job status updates through WebSockets

### Health
- `GET /health` - Server health check with WebSocket connections info

## Author

Created by Yavuz Topsever (https://github.com/yavuztopsever)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
