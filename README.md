# Disco-Machina

AI-powered software development crew terminal client with chat and API server integration.

## Overview

Disco-Machina is a terminal client for interacting with AI-powered software development agents. It provides a user-friendly interface for creating projects, tracking progress, chatting with the Project Manager agent, and more.

## Key Features

- **Interactive Terminal Client**: Colorful ASCII art interface with command-line tools
- **Chat with Project Manager**: Directly communicate with the Project Manager agent
- **Multiple Specialized Agents**: Project Manager, Software Architect, Fullstack Developer, and Test Engineer
- **Complete Agile Development Process**: From requirements analysis to sprint retrospectives
- **Multiple Client Options**: Standard terminal client, simplified client, and robust client for all environments
- **Docker Support**: Easy deployment with Docker and healthcheck monitoring

## Installation

```bash
# Clone the repository
git clone https://github.com/yavuztopsever/disco-machina.git
cd disco-machina

# Run the installation script
./install.sh

# Or install manually
pip install -r requirements.txt
```

## Usage

### Terminal Client

```bash
# Start the chat with Project Manager
python terminal_client.py chat

# Create a new project
python terminal_client.py create --goal "Create a REST API for a blog" --interactive

# List all projects
python terminal_client.py list

# Get details for a specific project
python terminal_client.py get <job-id>

# Replay a specific task
python terminal_client.py replay <task-index>
```

### Alternative Clients

```bash
# Use the simple chat client
python simple_chat.py

# Use the robust chat client (works in all environments)
python robust_chat.py

# Test the chat functionality
python test_chat.py
```

### API Server

```bash
# Start the API server
python -m src.dev_team.server

# Use the API server
curl -X POST http://localhost:8000/projects -H "Content-Type: application/json" -d '{"project_goal": "Create a REST API", "codebase_dir": "/tmp/output"}'
```

### Docker Support

```bash
# Using docker-compose
docker-compose up

# Or run the Docker image directly
docker run -p 8000:8000 -v ./output:/app/output -e OPENAI_API_KEY=$OPENAI_API_KEY disco-machina
```

## Project Structure

The project is organized as follows:

- `terminal_client.py` - Main terminal client with all commands
- `simple_chat.py` - Simplified chat client
- `robust_chat.py` - Enhanced chat client for all environments
- `test_chat.py` - Test script for the chat functionality
- `src/dev_team/` - Main source code directory
  - `server.py` - API server implementation
  - `crew.py` - Implementation of the Dev Team crew
  - `tools/` - Tools used by the agents
  - `config/` - Configuration files
  - `docs/` - Technical documentation
- `docs/` - User documentation
  - `client_usage.md` - Terminal client usage guide
  - `terminal_interaction_guide.md` - Detailed interaction guide
  - `terminal_client_changes.md` - Changes summary

## Agent Capabilities

The AI team consists of four specialized agents organized in a hierarchical structure:

1. **Project Manager** (Leader)
   - Requirements analysis, sprint planning, documentation, team coordination
   - Direct chat interface through the terminal client

2. **Software Architect** (Technical Lead)
   - Architecture design, code structure analysis, refactoring, code cleanup

3. **Fullstack Developer** (Implementer)
   - Feature implementation, code generation, dependency management

4. **Test Engineer** (Quality Assurance)
   - Test creation, execution, code coverage, and code review

## Author

**Yavuz Topsever**
- GitHub: [https://github.com/yavuztopsever](https://github.com/yavuztopsever)

## License

[MIT License](LICENSE)# disco-machina
