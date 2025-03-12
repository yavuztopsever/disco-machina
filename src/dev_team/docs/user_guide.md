# Dev Team User Guide

This guide helps you get started with the Dev Team, a CrewAI-powered development crew that automates software development tasks using AI agents working in an Agile framework.

## Getting Started

### Requirements

- Python 3.8+
- CrewAI 0.100.0+ (for memory and planning features)
- OpenAI API key with access to GPT models and embedding models
- Sufficient disk space for memory storage

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd dev-team
   ```

2. Install dependencies:
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Or using Poetry
   poetry install
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

4. (Optional) Configure memory storage location:
   ```bash
   # Set custom directory for memory storage (default uses system appdir location)
   export CREWAI_STORAGE_DIR="./memory_storage"
   ```

### Basic Usage

Run the Dev Team with a project goal and codebase directory:

```bash
python -m src.dev_team.main run "Create a REST API for a blog" "./my_blog_project"
```

This will:
1. Initialize the Dev Team crew with five specialized AI agents
2. Execute the Agile development workflow in sequence
3. Request your feedback at the end of the sprint
4. Iterate to another sprint if feedback is provided

## Command-Line Options

The Dev Team supports several commands and options:

### Running the Crew

```bash
# Run with default settings
python -m src.dev_team.main run

# Run with specific project goal and directory
python -m src.dev_team.main run "Create a todo list application" "./todo_app"
```

### Training the Crew

```bash
# Train the crew for 3 iterations and save results
python -m src.dev_team.main train 3 "training_results.json" "Build a weather app" "./weather_app"
```

### Testing Different Models

```bash
# Test with a specific AI model for 2 iterations
python -m src.dev_team.main test 2 "gpt-4" "Create a data dashboard" "./dashboard_app"
```

### Replaying Tasks

```bash
# Replay a specific task (by index)
python -m src.dev_team.main replay 0
```

### Managing Memory

```bash
# Reset all memory types
python -m src.dev_team.main reset-memory all

# Reset specific memory type
python -m src.dev_team.main reset-memory long   # Reset long-term memory
python -m src.dev_team.main reset-memory short  # Reset short-term memory 
python -m src.dev_team.main reset-memory entities  # Reset entity memory
python -m src.dev_team.main reset-memory knowledge  # Reset knowledge storage
```

## Understanding the Output

During execution, the Dev Team will:

1. Create a `results` directory in your codebase directory
2. Organize outputs by sprint number
3. Save task outputs as JSON files
4. Generate a comprehensive sprint result file

The output structure looks like:

```
my_project/
└── results/
    ├── sprint_1/
    │   ├── requirements_analysis_task_output.json
    │   ├── architecture_design_task_output.json
    │   └── ...
    └── sprint_2/
        ├── requirements_analysis_task_output.json
        ├── architecture_design_task_output.json
        └── ...
```

## Providing Effective Feedback

At the end of each sprint, you'll be prompted to provide feedback. For best results:

1. **Be Specific**: Mention specific aspects of the implementation
2. **Prioritize Issues**: Indicate which issues are most important
3. **Suggest Improvements**: Provide ideas for enhancements
4. **Set Expectations**: Clarify what you expect in the next sprint

Example of effective feedback:
```
The API design looks good, but I'd like to see more comprehensive error handling.
The database schema needs normalization. For the next sprint, prioritize adding 
user authentication and implementing the comment feature.
```

## Customizing the Dev Team

### Modifying Agent Configuration

Edit `src/dev_team/config/agents.yaml` to:
- Change agent roles and responsibilities
- Adjust tool assignments
- Modify delegation permissions

### Customizing Tasks

Edit `src/dev_team/config/tasks.yaml` to:
- Add or remove tasks
- Change task dependencies
- Reassign tasks to different agents
- Modify task priorities

### Adding New Tools

Extend the Dev Team's capabilities by implementing new tools in `src/dev_team/tools/dev_tools.py`.

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your OpenAI API key is set correctly
   - Check if your API key has sufficient quota

2. **Dependency Issues**
   - Make sure all dependencies are installed
   - Check Python version compatibility (3.8+ required)

3. **Task Execution Failures**
   - Check task dependencies in configuration
   - Ensure file paths are correct and accessible

### Getting Help

If you encounter issues:
1. Check the logs (standard output and error)
2. Examine the task output JSON files
3. Create an issue in the repository with detailed information

## Advanced Features

### Planning System

The Dev Team uses CrewAI's planning capabilities to improve task execution and performance:

- Before each task is executed, a detailed step-by-step plan is created
- These plans are added to task descriptions to provide better guidance
- The same language model is used for planning and execution for consistency

Benefits of the planning system:
- More methodical approach to complex development tasks
- Better task coordination between agents
- Reduced redundancy in implementations
- Improved focus on project goals

### Memory System

The Dev Team implements a sophisticated memory system that enhances agent capabilities:

**Memory Types:**
- **Short-Term Memory**: Stores recent interactions and outputs using RAG (Retrieval Augmented Generation)
- **Long-Term Memory**: Preserves insights from past sprints in a persistent database
- **Entity Memory**: Captures information about code entities (classes, functions, variables)
- **Contextual Memory**: Maintains conversation context between tasks and sprints

**Benefits:**
- Agents learn from past sprint experiences
- Better understanding of the codebase structure
- Improved continuity between sprints
- More contextual awareness in agent interactions

**Managing Memory Programmatically:**
```python
from src.dev_team.crew import DevTeamCrew

# Create crew
crew = DevTeamCrew()

# Reset specific memory type
crew.reset_memories("long")    # Reset long-term memory
crew.reset_memories("short")   # Reset short-term memory
crew.reset_memories("entities") # Reset entity memory
crew.reset_memories("all")     # Reset all memory types
```

### Human Input Integration

The Dev Team offers interactive human-in-the-loop collaboration through direct input at critical stages:

**Key Features:**
- Agents prompt for human feedback at strategic decision points
- Implementation and testing tasks actively request user input
- Questions are specific and contextual to the current task
- Human expertise directly influences agent decisions in real-time

**How It Works:**
1. The agent begins working on a task (e.g., implementing a feature)
2. At critical decision points, it pauses and asks for your input
3. You provide guidance, suggestions, or approve the proposed approach
4. The agent incorporates your feedback and continues with the task

**Benefits:**
- Higher quality implementations with human oversight
- Better alignment between implementation and expectations
- Fewer iterations required to achieve desired results
- Knowledge sharing between human experts and AI agents

### Code Execution

The Dev Team includes code execution capabilities for developers and test engineers:

**Key Features:**
- Agents can write and execute Python code in real-time
- Support for data analysis libraries (numpy, pandas, matplotlib)
- Safe execution environment with proper error handling
- Automatic retry with corrections when code fails

**Example Use Cases:**
- Generating test data for feature testing
- Creating data structures and algorithms for implementation
- Analyzing code metrics and complexity
- Automating repetitive coding tasks
- Validating implementations through direct execution

**Benefits:**
- Faster implementation of complex logic
- More accurate testing through executable validation
- Dynamic problem-solving capabilities
- Immediate verification of solution correctness

### Using the Dev Team as a Library

You can import and use the Dev Team in your own code:

```python
from src.dev_team.crew import DevTeamCrew

# Create and configure the crew
crew = DevTeamCrew()

# Run the crew with custom settings
result = crew.run("Build a REST API", "./my_api_project")

# Access the results
print(result)

# Reset memories if needed
crew.reset_memories("all")
```

### Extending with Custom Agents

You can extend the Dev Team with your own custom agents:

1. Define the agent in `agents.yaml`
2. Create custom tools for the agent
3. Update the hierarchical order in `crew.py`
4. Add tasks for the agent in `tasks.yaml`

## Best Practices

For optimal results with the Dev Team:

1. **Clear Project Goals**: Define specific, achievable project goals
2. **Structured Codebase**: Maintain a well-organized directory structure
3. **Incremental Development**: Focus on small, manageable features
4. **Regular Feedback**: Provide detailed feedback after each sprint
5. **Documentation**: Keep documentation up-to-date

## Example Workflows

### Web Application Development

```bash
python -m src.dev_team.main run "Create a React frontend with user authentication" "./web_app"
```

### API Development

```bash
python -m src.dev_team.main run "Build a RESTful API with Flask and SQLAlchemy" "./api_project"
```

### Code Refactoring

```bash
python -m src.dev_team.main run "Refactor legacy code and improve test coverage" "./legacy_app"
```

## Conclusion

The Dev Team provides an automated, Agile approach to software development using AI agents. By following this guide, you can effectively use the Dev Team to assist with various development tasks, from initial requirements to implementation and testing.