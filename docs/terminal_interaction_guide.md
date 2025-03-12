# DiscoMachina Terminal Interaction Guide

DiscoMachina is a powerful terminal interface for interacting with AI-powered Dev Team agents. This guide provides step-by-step instructions for installation and use.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Command Reference](#command-reference)
- [Interactive Features](#interactive-features)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Troubleshooting](#troubleshooting)

## Installation

### Step 1: Install DiscoMachina

Run the installer script:

```bash
# Navigate to your Dev Team project directory
cd /Volumes/HomeX/yavuztopsever/Projects/dev_team

# Run the installer
./install.sh   # Or use the path to the installer: ~/discomachina-installer.sh
```

### Step 2: Update Your PATH

After installation, update your shell configuration:

```bash
# For Zsh users (macOS default)
source ~/.zshrc

# For Bash users
source ~/.bash_profile
```

### Step 3: Verify Installation

Check that DiscoMachina is properly installed:

```bash
which discomachina   # Should show the path to the command
discomachina --version
```

## Basic Usage

### Starting DiscoMachina

Navigate to any project directory and launch DiscoMachina:

```bash
# Navigate to your project
cd /path/to/your/project

# Launch DiscoMachina
discomachina
```

The tool will:
1. Display a colorful ASCII art intro
2. Check if the Dev Team API server is running
3. Start the server if needed
4. Use your current directory as the codebase path

### Starting a Chat Session

The most direct way to interact with the AI is through the chat mode:

```bash
discomachina chat
```

This opens an interactive chat session with the Project Manager agent where you can:
- Ask questions about your codebase
- Request research on specific topics
- Brainstorm ideas and solutions
- Give specific tasks to analyze or explore code

Example chat session:
```
[Project Manager] How can I help you today?

[You] Can you analyze the structure of this codebase and tell me what it does?

[Project Manager] I'll analyze this codebase for you. Let me explore the directory structure first...
```

To exit chat mode, simply type `exit`, `quit`, or `bye`.

### Creating a New Project

To analyze or work with your current codebase:

```bash
discomachina create --goal "Your project goal description" --interactive
```

For example:

```bash
discomachina create --goal "Analyze this codebase and provide suggestions for improvement" --interactive
```

The `--interactive` flag enables communication with the agents during execution.

### Listing Projects

To see all running or completed projects:

```bash
discomachina list
```

### Checking Project Status

To check the status of a specific project:

```bash
discomachina get <job_id>
```

Replace `<job_id>` with the ID returned when you created the project.

### Replaying Tasks

To replay a specific task:

```bash
discomachina replay <task_index>
```

Replace `<task_index>` with the index of the task you want to replay.

## Command Reference

DiscoMachina supports the following commands:

| Command | Description | Example |
|---------|-------------|---------|
| `chat` | Chat with the Project Manager | `discomachina chat` |
| `create` | Create a new project | `discomachina create --goal "Analyze code" --interactive` |
| `list` | List all projects | `discomachina list` |
| `get` | Get project status | `discomachina get 12345-abcde` |
| `replay` | Replay a specific task | `discomachina replay 2` |
| `reset` | Reset agent memory | `discomachina reset --type all` |
| `compact` | Manually compact context | `discomachina compact` |

### Chat Command Options

The `chat` command has optional parameters:

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--model` | Specify AI model to use | No | System default |

Example:

```bash
discomachina chat --model gpt-4o
```

### Create Command Options

The `create` command has several options:

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--goal` | The project goal description | Yes | None |
| `--dir` | Codebase directory | No | Current directory |
| `--interactive` | Enable interactive mode | No | False |

Example:

```bash
discomachina create --goal "Create unit tests for all functions" --interactive
```

## Interactive Features

### Color-Coded Output

DiscoMachina uses color-coding to make output more readable:

- **Blue**: Informational messages
- **Green**: Success messages
- **Red**: Error messages
- **Orange**: Warning messages
- **Purple**: System messages

### Progress Indicators

The tool shows real-time progress using:

- Animated progress bars
- Spinning indicators for ongoing tasks
- Color-coded status updates

### Context Management

DiscoMachina automatically manages the conversation context:

- Tracks token usage
- Automatically compacts context when needed
- Preserves recent messages during compaction

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Manually compact context |
| `Ctrl+C` | Exit DiscoMachina |

## Troubleshooting

### Server Connection Issues

If DiscoMachina can't connect to the Dev Team API server:

```bash
# Check if the server is running
ps aux | grep "dev_team.server"

# Manually start the server
cd /Volumes/HomeX/yavuztopsever/Projects/dev_team
python -m src.dev_team.main server
```

### Path Issues

If the `discomachina` command is not found:

```bash
# Check if ~/bin is in your PATH
echo $PATH

# If not, add it manually
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Context Window Errors

If you encounter context window errors:

```bash
# Manually compact the context
discomachina compact
```

### Terminal Color Support

If colors aren't displaying correctly:

```bash
# Check terminal color support
echo $TERM

# Set terminal to support colors
export TERM=xterm-256color
```