# Dev Team Project Information

## Common Commands

### Installation

```bash
# Install dependencies using pip
pip install -r requirements.txt

# Or using Poetry
poetry install
```

### Running the Dev Team Crew

```bash
# Run with default settings
python -m src.dev_team.main run

# Run with specific project goal and directory
python -m src.dev_team.main run "Create a REST API for a blog" "./my_blog_project"

# Train the crew
python -m src.dev_team.main train 3 "training_results.json" "Your project goal" "/path/to/codebase/directory"

# Test with a specific model
python -m src.dev_team.main test 2 "gpt-4" "Your project goal" "/path/to/codebase/directory"

# Replay a specific task
python -m src.dev_team.main replay 0
```

## Project Structure

The project is organized as follows:

- `src/dev_team/` - Main source code directory
  - `main.py` - Entry point with command-line interface
  - `crew.py` - Implementation of the Dev Team crew
  - `tools/` - Tools used by the agents
    - `dev_tools.py` - Implementation of agent tools
  - `config/` - Configuration files
    - `agents.yaml` - Agent definitions and roles
    - `tasks.yaml` - Task definitions with dependencies
  - `docs/` - Documentation
    - `implementation.md` - Technical implementation details
    - `user_guide.md` - User guide for getting started

## Agents and Roles

The Dev Team consists of four specialized agents organized in a hierarchical structure:

1. **Project Manager** (Leader)
   - Requirements analysis, sprint planning, documentation, team coordination
   - Domain-specific Tools: RequirementsAnalysisTool, TaskTrackingTool, AgileProjectManagementTool
   - CrewAI Tools: BraveSearchTool, DirectoryReadTool, FileReadTool, FileWriterTool, GithubSearchTool

2. **Software Architect** (Technical Lead)
   - Architecture design, code structure analysis, refactoring, code cleanup
   - Domain-specific Tools: CodeAnalysisTool, CodebaseAnalysisTool, CodeRefactoringTool, ObsoleteCodeCleanupTool
   - CrewAI Tools: CodeDocsSearchTool, DirectoryReadTool, FileReadTool, FileWriterTool, GithubSearchTool

3. **Fullstack Developer** (Implementer)
   - Feature implementation, code generation, dependency management
   - Domain-specific Tools: CodeImplementationTool, CodeGenerationTool, DependencyManagementTool
   - CrewAI Tools: CodeInterpreterTool, CodeDocsSearchTool, DirectoryReadTool, FileReadTool, FileWriterTool, GithubSearchTool, BraveSearchTool

4. **Test Engineer** (Quality Assurance)
   - Test creation, execution, code coverage, and code review
   - Domain-specific Tools: TestGenerationTool, TestRunnerTool, CodeCoverageTool, CodeReviewTool
   - CrewAI Tools: CodeInterpreterTool, DirectoryReadTool, FileReadTool, FileWriterTool, CodeDocsSearchTool, GithubSearchTool

## Agile Workflow

The crew follows a complete Agile development process with the following workflow:

1. **Requirements Analysis**: Create product backlog with user stories and acceptance criteria
2. **Architecture Design**: Design system components, organization, and data flow
3. **Codebase Analysis**: Analyze existing code structure and identify improvements
4. **Sprint Planning**: Create sprint plan with prioritized backlog items
5. **Feature Implementation**: Implement features according to sprint plan
6. **Test Development**: Write tests for implemented features
7. **Code Review**: Review code against quality standards
8. **Code Refactoring**: Improve code structure and reduce complexity
9. **Code Cleanup**: Remove obsolete code and dependencies
10. **Documentation Update**: Update documentation to reflect changes
11. **Sprint Retrospective**: Analyze sprint outcomes and plan improvements

## Code Style Preferences

- **Python**: We follow PEP 8 style guidelines
- **Documentation**: Use Google-style docstrings for functions and classes
- **Naming Conventions**: 
  - snake_case for variables and functions
  - PascalCase for classes
  - UPPER_CASE for constants
- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 88 characters
- **Imports**: Group standard library, third-party, and local imports with a blank line between groups

## Hierarchical Process Implementation

The crew uses CrewAI's hierarchical process for better task delegation and coordination:

1. **Leadership Layer**: Project Manager as team lead
2. **Architecture Layer**: Software Architect as technical authority
3. **Implementation Layer**: Fullstack Developer and Test Engineer as implementers
4. **Feedback Layer**: Feedback Collector for user input

## Sprint-Based Development

The Dev Team operates in sprints, with each sprint having:

1. **Sprint Initialization**: Define goals and create output directory
2. **Task Execution**: Execute tasks in dependency order
3. **User Feedback**: Collect feedback at sprint completion
4. **Sprint Iteration**: Increment sprint number and adjust based on feedback

## CrewAI Tools Integration

The Dev Team now leverages built-in CrewAI tools for enhanced capabilities:

1. **BraveSearchTool** - Enables web search capabilities through the Brave Search API
   - Used for: Market research, finding documentation, and researching technical solutions

2. **CodeDocsSearchTool** - Provides semantic search within code documentation
   - Used for: Finding API references, language documentation, and framework guides

3. **CodeInterpreterTool** - Executes Python code in a secure container
   - Used for: Testing code snippets, prototyping solutions, and data analysis

4. **DirectoryReadTool** - Lists directory contents with enhanced features
   - Used for: Exploring codebase structure and finding relevant files

5. **FileReadTool** - Reads file contents with improved error handling
   - Used for: Accessing code files, configuration files, and documentation

6. **FileWriterTool** - Writes content to files with cross-platform compatibility
   - Used for: Creating and updating code files, documentation, and configuration

7. **GithubSearchTool** - Provides semantic search for GitHub repositories
   - Used for: Finding examples, solutions, and best practices from GitHub

## Useful Information

- The project uses CrewAI 0.105.0+ with crewai-tools 0.33.0+
- Custom tools are implemented as CrewAI Tool decorators
- Built-in CrewAI tools are used for web search, RAG, and file operations
- Tasks use the context system to maintain state between tasks
- The crew uses hierarchical process for better task delegation
- Output is organized by sprint number in the results directory
- Token usage is optimized with smart model selection
- Error recovery is implemented with exponential backoff and checkpointing
- Human input incorporates timeout handling and terminal detection
- File operations include backup mechanisms and permission checking