from pathlib import Path
import yaml
from crewai import Agent, Task, Crew, Process
from typing import Dict, List, Any, Optional, Callable
import os
import platform
import subprocess
from datetime import datetime
from .tools import (
    # Custom tools
    CodeAnalysisTool,
    CodeImplementationTool,
    CodeReviewTool,
    RequirementsAnalysisTool,
    TaskTrackingTool,
    TestGenerationTool,
    TestRunnerTool,
    CodeCoverageTool,
    CodeGenerationTool,
    DependencyManagementTool,
    CodebaseAnalysisTool,
    CodeRefactoringTool,
    ObsoleteCodeCleanupTool,
    AgileProjectManagementTool,
    # CrewAI tools
    brave_search_tool,
    code_docs_search_tool,
    code_interpreter_tool,
    directory_read_tool,
    file_read_tool,
    file_writer_tool,
    github_search_tool,
    CREWAI_TOOLS
)

class DevTeamCrew:
    def __init__(self, config_dir: Optional[str] = None):
        # Token and model management
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        
        # Model selection based on task complexity
        self.available_models = {
            "large": "openai/gpt-4",
            "medium": "openai/gpt-4o-mini",
            "small": "openai/gpt-3.5-turbo"
        }
        
        # Default to medium model with constraints
        self.llm_config = {
            "model": self.available_models["medium"],
            "temperature": 0.7,
            "request_timeout": 600,
            "max_tokens": 4000,  # Limit output tokens
            "context_window_fallback": True  # Enable context window management
        }
        
        # Max tokens per request to avoid rate limits
        self.max_tokens_per_request = 100000
        
        # Basic configuration
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent / "config"
        self.agents_config = self._load_config("agents.yaml")
        self.tasks_config = self._load_config("tasks.yaml")
        self.tools = self._initialize_tools()
        self.project_goal = ""
        self.codebase_dir = ""
        self.user_feedback = ""
        self.sprint_number = 1
        self.active_crew = None  # Will hold reference to the current active crew
        
        # Cache for already processed content
        self.content_cache = {}
        
        # Ensure we have admin access
        self._ensure_admin_access()

    def _load_config(self, filename: str) -> dict:
        with open(self.config_dir / filename, "r") as f:
            return yaml.safe_load(f)

    def _ensure_admin_access(self):
        """Ensure the agents have appropriate access to files and directories"""
        try:
            # Ensure target directories have appropriate permissions
            if not os.path.exists(self.codebase_dir) and self.codebase_dir:
                os.makedirs(self.codebase_dir, exist_ok=True)
                
            # Check if we're running with admin/sudo privileges
            is_admin = False
            if platform.system() == 'Windows':
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:  # Unix-like systems (Linux, macOS)
                is_admin = os.geteuid() == 0 if hasattr(os, 'geteuid') else True
                
            if not is_admin:
                print("Warning: Running without admin privileges. Some file operations may be restricted.")
                print("For full functionality, consider running with elevated privileges.")
                
            # Ensure required directories are writable
            self._ensure_directory_access(str(self.config_dir))
            if self.codebase_dir:
                self._ensure_directory_access(self.codebase_dir)
                
        except Exception as e:
            print(f"Warning: Failed to verify admin access: {str(e)}")
    
    def _ensure_directory_access(self, directory):
        """Ensure a directory is accessible and writable"""
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Try to create a test file to verify write permissions
        test_file = os.path.join(directory, ".test_write_access")
        try:
            with open(test_file, 'w') as f:
                f.write("Test write access")
            os.remove(test_file)
        except Exception as e:
            print(f"Warning: Directory {directory} is not writable: {str(e)}")
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = os.path.join(os.path.dirname(__file__), "config", filename)
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading configuration from {config_path}: {str(e)}")
            # Return empty config as fallback
            return {}
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize all available tools"""
        # Start with custom tools
        tools = {
            "CodeAnalysisTool": CodeAnalysisTool(),
            "CodeImplementationTool": CodeImplementationTool(),
            "CodeReviewTool": CodeReviewTool(),
            "RequirementsAnalysisTool": RequirementsAnalysisTool(),
            "TaskTrackingTool": TaskTrackingTool(),
            "TestGenerationTool": TestGenerationTool(),
            "TestRunnerTool": TestRunnerTool(),
            "CodeCoverageTool": CodeCoverageTool(),
            "CodeGenerationTool": CodeGenerationTool(),
            "DependencyManagementTool": DependencyManagementTool(),
            "CodebaseAnalysisTool": CodebaseAnalysisTool(),
            "CodeRefactoringTool": CodeRefactoringTool(),
            "ObsoleteCodeCleanupTool": ObsoleteCodeCleanupTool(),
            "AgileProjectManagementTool": AgileProjectManagementTool()
        }
        
        # Add CrewAI tools for web search, RAG, and file operations
        tools.update({
            "BraveSearchTool": brave_search_tool,
            "CodeDocsSearchTool": code_docs_search_tool,
            "CodeInterpreterTool": code_interpreter_tool,
            "DirectoryReadTool": directory_read_tool,
            "FileReadTool": file_read_tool,
            "FileWriterTool": file_writer_tool,
            "GithubSearchTool": github_search_tool
        })
        
        return tools

    def _get_agent_tools(self, agent_config: Dict[str, Any]) -> List[Any]:
        """Get the tools for an agent based on their configuration"""
        agent_tools = []
        if "tools" in agent_config:
            for tool_name in agent_config["tools"]:
                if tool_name in self.tools:
                    agent_tools.append(self.tools[tool_name])
        return agent_tools

    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text string
        
        This is a simple estimation method. For production use, consider using
        more accurate tokenizers like tiktoken for OpenAI models.
        """
        # Simple approximation: 1 token ~= 4 chars for English text
        return len(text) // 4
    
    def select_model_for_complexity(self, task_description: str, role: str) -> str:
        """Select appropriate model based on task complexity and agent role
        
        Args:
            task_description: The task description to analyze
            role: The role of the agent (used to determine if complex models are needed)
        
        Returns:
            model_name: The name of the selected model
        """
        # Estimate tokens in the task description
        estimated_tokens = self.estimate_tokens(task_description)
        
        # Leadership roles always get more powerful models
        if role in ["Project Manager", "Software Architect"]:
            if estimated_tokens > 10000:
                return self.available_models["large"]
            return self.available_models["medium"]
            
        # For implementation tasks, use model based on complexity
        complexity_indicators = ["complex", "difficult", "challenging", "advanced"]
        has_complexity = any(indicator in task_description.lower() for indicator in complexity_indicators)
        
        if estimated_tokens > 15000 or has_complexity:
            return self.available_models["medium"]
        else:
            return self.available_models["small"]
    
    def get_agents(self) -> Dict[str, Agent]:
        """Create and return all agents based on their configuration"""
        agents = {}
        
        # Create standard agents from config with enhanced capabilities
        for agent_id, config in self.agents_config.items():
            # Determine if this agent should have delegation capability
            # Project Manager and Software Architect should always have delegation
            is_leader = agent_id in ["project_manager", "software_architect"]
            allow_delegation = config.get("allow_delegation", False) or is_leader
            
            # Determine appropriate memory settings - always enable for complex tasks
            memory_enabled = config.get("memory", True)
            
            # Get code execution settings from config or use defaults
            allow_code_execution = config.get("allow_code_execution", False)
            code_execution_mode = config.get("code_execution_mode", "safe")
            max_retry_limit = config.get("max_retry_limit", 3)
            
            # Set max iterations based on role complexity
            if agent_id == "project_manager":
                max_iter = 30  # More iterations for complex planning
            elif agent_id in ["software_architect", "fullstack_developer"]:
                max_iter = 25  # Medium iterations for development
            else:
                max_iter = 20  # Standard iterations for other roles
            
            # Use a separate copy of llm_config for each agent to avoid shared state
            agent_llm_config = self.llm_config.copy()
            
            # Select model based on agent's role and expected tasks
            role_name = config["name"]
            sample_task = "Perform standard tasks related to " + config["role"]
            agent_llm_config["model"] = self.select_model_for_complexity(sample_task, role_name)
            
            # Get agent tools - first check if CodeInterpreterTool is in the tools list
            tools = self._get_agent_tools(config)
            # Check if the tool has the same name as the CodeInterpreterTool
            has_code_interpreter = any(getattr(tool, 'name', '') == 'Code Interpreter' for tool in tools)
            
            # Create the agent with enhanced attributes
            agent = Agent(
                name=config["name"],
                role=config["role"],
                goal=config["goal"],
                backstory=config["backstory"],
                verbose=config["verbose"],
                allow_delegation=allow_delegation,
                temperature=config["temperature"],
                memory=memory_enabled,
                tools=tools,
                llm_config=agent_llm_config,  # Use agent-specific LLM config
                max_iter=max_iter,  # Set iterations based on role
                # Only set allow_code_execution if CodeInterpreterTool is not in tools
                # (to avoid duplicate code execution capabilities)
                allow_code_execution=allow_code_execution and not has_code_interpreter,
                code_execution_mode=code_execution_mode,
                respect_context_window=True,  # Prevent context window issues
                max_retry_limit=max_retry_limit  # Use config value or default
            )
            agents[agent_id] = agent
            
            # Log model selection
            print(f"Agent '{role_name}' using model: {agent_llm_config['model']}")
        
        return agents
    
    def get_hierarchical_agent_order(self) -> List[str]:
        """Define the hierarchical order of agents for the CrewAI hierarchical process"""
        # Order matters for hierarchical process - define leader first, then subordinates
        # The first agent acts as the crew manager with delegation authority
        
        # Check which agents are available in the current configuration
        available_agents = list(self.agents_config.keys())
        
        # Define the ideal order with fallbacks
        ideal_order = [
            "project_manager",     # Primary leader/coordinator role
            "software_architect",  # Technical lead with architectural authority
            "fullstack_developer", # Implementation specialist
            "test_engineer"        # Quality assurance expert
        ]
        
        # Filter the order to include only available agents
        ordered_agents = [agent for agent in ideal_order if agent in available_agents]
        
        # If no project manager, make software architect the leader
        if "project_manager" not in available_agents and "software_architect" in available_agents:
            # Move software architect to the front if it exists
            ordered_agents.remove("software_architect")
            ordered_agents.insert(0, "software_architect")
        
        # Ensure we have at least one agent
        if not ordered_agents and available_agents:
            # Just use the first available agent as leader
            ordered_agents = [available_agents[0]]
            
        return ordered_agents

    def get_tasks(self, project_goal: str, codebase_dir: str) -> List[Task]:
        """Create and return all tasks based on the configuration, with enhanced collaboration"""
        self.project_goal = project_goal
        self.codebase_dir = codebase_dir
        
        # Ensure codebase directory exists
        if not os.path.exists(codebase_dir):
            os.makedirs(codebase_dir, exist_ok=True)
        
        tasks = []
        agents = self.get_agents()
        task_dict = {}  # Dictionary to store tasks by ID for dependency resolution
        
        # Create standard tasks from config with improved collaboration structure
        for task_id, config in self.tasks_config.items():
            # Replace placeholders in the task description and expected output
            description = config["description"].format(
                project_goal=project_goal,
                codebase_dir=codebase_dir,
                user_feedback=self.user_feedback,
                sprint_number=self.sprint_number
            )
            expected_output = config["expected_output"].format(
                project_goal=project_goal,
                codebase_dir=codebase_dir,
                sprint_number=self.sprint_number
            )
            
            # Get the agent for this task
            agent_id = config["agent"]
            if agent_id not in agents:
                # Try to find an appropriate fallback agent by role
                # If the original agent isn't available, reassign task to suitable alternative
                if agent_id == "project_manager" and "software_architect" in agents:
                    agent_id = "software_architect"
                elif agent_id == "software_architect" and "fullstack_developer" in agents:
                    agent_id = "fullstack_developer"
                elif agent_id == "test_engineer" and "fullstack_developer" in agents:
                    agent_id = "fullstack_developer"
                elif agent_id == "fullstack_developer" and "software_architect" in agents:
                    agent_id = "software_architect"
                else:
                    # Just use the first available agent if specific ones not found
                    agent_id = list(agents.keys())[0]
                
                # Log the reassignment
                print(f"Warning: Agent '{config['agent']}' not found for task '{task_id}'. Reassigned to '{agent_id}'")
            
            # Get the task dependencies first
            task_dependencies = []
            if "dependencies" in config and config["dependencies"]:
                for dep_id in config["dependencies"]:
                    # If the dependency is a string (task_id), look it up in the task_dict
                    if isinstance(dep_id, str) and dep_id in task_dict:
                        task_dependencies.append(task_dict[dep_id])
                    # If the dependency is an integer (index), look it up in the tasks list
                    elif isinstance(dep_id, int) and 0 <= dep_id < len(tasks):
                        task_dependencies.append(tasks[dep_id])
                    else:
                        print(f"Warning: Invalid dependency '{dep_id}' for task '{task_id}', ignoring.")
                        continue
            
            # Set up output file path in the results directory under the appropriate sprint
            results_dir = os.path.join(self.codebase_dir, "results", f"sprint_{self.sprint_number}")
            os.makedirs(results_dir, exist_ok=True)
            output_file = os.path.join(results_dir, f"{task_id}_output.json")
            
            # Check if task requires human input
            human_input = config.get("human_input", False)
            
            # Disable human input if in non-interactive mode
            if hasattr(self, 'non_interactive') and self.non_interactive and human_input:
                print(f"Note: Task '{task_id}' has human_input=True but running in non-interactive mode. Human input will be skipped.")
                # We still create the task with human_input=True to maintain the task definition,
                # but the CrewAI will handle this based on the crew's inputs parameter
            
            # Create task with additional collaborative features without callback
            # Callbacks have changed in newer CrewAI versions, so we'll log manually
            task = Task(
                description=description,
                expected_output=expected_output,
                agent=agents[agent_id],
                context=task_dependencies if task_dependencies else None,
                output_file=output_file,
                create_directory=True,  # Ensure the output directory exists
                human_input=human_input  # Enable human input if specified
            )
            
            # Log the task creation
            print(f"Created task: {task_id} assigned to {agent_id}")
            
            # We can't add custom attributes to Task objects in newer CrewAI versions
            # So we'll use a task ID map instead
            self.task_id_map = getattr(self, 'task_id_map', {})
            self.task_id_map[id(task)] = task_id
            tasks.append(task)
            task_dict[task_id] = task
        
        # We no longer use a separate feedback agent
        # Human input is collected directly in relevant tasks via the human_input flag
        
        return tasks
        
    def _task_completion_callback(self, task_id: str, output: Any) -> None:
        """Handle task completion and prepare for next tasks"""
        try:
            print(f"Task '{task_id}' completed. Preparing for dependent tasks...")
            
            # Here we could implement additional inter-task communication
            # or special handling based on task outputs
            
            # For now, just log completion
            log_file = os.path.join(self.codebase_dir, "results", f"sprint_{self.sprint_number}", "task_log.txt")
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            with open(log_file, "a") as f:
                f.write(f"Task '{task_id}' completed at {datetime.now().isoformat()}\n")
        
        except Exception as e:
            print(f"Warning: Error in task completion callback: {str(e)}")

    def is_terminal_interactive(self) -> bool:
        """Check if the terminal is interactive
        
        Returns:
            bool: True if the terminal is interactive
        """
        # Check if stdin is a tty and process is not daemonized
        import sys
        return sys.stdin.isatty() and os.getppid() != 1
    
    def input_with_timeout(self, prompt: str, timeout: int = 60, default: str = "") -> str:
        """Get user input with timeout
        
        Args:
            prompt: Input prompt to display
            timeout: Timeout in seconds
            default: Default value to return if timeout occurs
            
        Returns:
            User input or default if timeout occurs
        """
        # Import here to avoid dependencies in the main code
        import threading
        import signal
        
        # When timeout occurs, raise an exception in the main thread
        def timeout_handler(signum, frame):
            raise TimeoutError("Input timed out")
        
        # Only set the alarm if the terminal is interactive
        if self.is_terminal_interactive():
            print(prompt)
            
            # Set alarm for timeout
            try:
                # Previous alarm handler
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                # Set timeout alarm
                signal.alarm(timeout)
                
                try:
                    # Get input
                    user_input = input()
                    return user_input
                finally:
                    # Cancel alarm and restore handler
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
            except TimeoutError:
                print(f"\nInput timed out after {timeout} seconds. Using default value.")
                return default
            except Exception as e:
                print(f"\nError getting input: {str(e)}. Using default value.")
                return default
        else:
            # If in non-interactive mode, just return the default
            return default
    
    def collect_user_feedback(self, non_interactive: bool = False) -> str:
        """Collect feedback from the user at the end of a sprint with enhanced input handling
        
        Args:
            non_interactive: If True, don't prompt for input and use default feedback
            
        Returns:
            User feedback or default feedback
        """
        print("\n" + "="*50)
        print(f"SPRINT {self.sprint_number} COMPLETED")
        print("="*50)
        print(f"Project Goal: {self.project_goal}")
        
        # Default feedback
        default_feedback = f"Auto-generated feedback for sprint {self.sprint_number}: Continue development."
        
        # Determine if we should attempt to get user input
        should_get_input = not non_interactive and self.is_terminal_interactive()
        
        if should_get_input:
            print("\nWould you like to continue to the next sprint?")
            try:
                # Get input with timeout
                feedback = self.input_with_timeout(
                    prompt="\nProvide any additional feedback for the next sprint (or press Enter to skip): ",
                    timeout=60,  # 60 second timeout
                    default=default_feedback
                )
                
                # If empty, use default
                if not feedback.strip():
                    feedback = default_feedback
                    print(f"No feedback provided. Using default: '{feedback}'")
            except Exception as e:
                # Handle any errors
                feedback = default_feedback
                print(f"\nError getting feedback: {str(e)}. Using default: '{feedback}'")
        else:
            # In non-interactive mode, use default feedback
            feedback = default_feedback
            if non_interactive:
                reason = "non-interactive mode"
            elif not self.is_terminal_interactive():
                reason = "non-interactive terminal"
            else:
                reason = "unknown reason"
                
            print(f"\nRunning in {reason}. Using default feedback: '{feedback}'")
        
        # Store feedback
        self.user_feedback = feedback
        
        if feedback.strip():
            print("\nFeedback will be incorporated into the next sprint planning.")
        
        print("="*50 + "\n")
        
        return feedback

    def setup_output_directory(self) -> Dict[str, Any]:
        """Set up the directory structure for storing task outputs
        
        Returns:
            Dict with status information
        """
        result = {
            "success": True,
            "message": "",
            "directories_created": []
        }
        
        # Create the results directory
        results_dir = os.path.join(self.codebase_dir, "results")
        dir_result = self.create_directory_safely(results_dir)
        if not dir_result["success"]:
            result["success"] = False
            result["message"] = f"Failed to create results directory: {dir_result['message']}"
            return result
        result["directories_created"].append(results_dir)
        
        # Create the sprint directory
        sprint_dir = os.path.join(results_dir, f"sprint_{self.sprint_number}")
        dir_result = self.create_directory_safely(sprint_dir)
        if not dir_result["success"]:
            result["success"] = False
            result["message"] = f"Failed to create sprint directory: {dir_result['message']}"
            return result
        result["directories_created"].append(sprint_dir)
        
        # Create additional directories
        src_dir = os.path.join(self.codebase_dir, "src")
        self.create_directory_safely(src_dir)
        result["directories_created"].append(src_dir)
        
        tests_dir = os.path.join(self.codebase_dir, "tests")
        self.create_directory_safely(tests_dir)
        result["directories_created"].append(tests_dir)
        
        docs_dir = os.path.join(self.codebase_dir, "docs")
        self.create_directory_safely(docs_dir)
        result["directories_created"].append(docs_dir)
        
        return result

    def update_token_usage(self, response_info):
        """Update token usage statistics from LLM response
        
        Args:
            response_info: The response object from the LLM that contains token usage information
        """
        # Update token counts if available
        if hasattr(response_info, 'usage'):
            usage = response_info.usage
            self.token_usage["prompt_tokens"] += getattr(usage, "prompt_tokens", 0)
            self.token_usage["completion_tokens"] += getattr(usage, "completion_tokens", 0)
            self.token_usage["total_tokens"] += getattr(usage, "total_tokens", 0)
            
            # Log current usage
            print(f"Current token usage: {self.token_usage}")
    
    def check_directory_permissions(self, directory: str) -> Dict[str, bool]:
        """Check if we have read/write/execute permissions for a directory
        
        Args:
            directory: Directory path to check
            
        Returns:
            Dict with permission status
        """
        permissions = {
            "readable": False,
            "writable": False,
            "executable": False,
            "exists": os.path.exists(directory)
        }
        
        if permissions["exists"]:
            permissions["readable"] = os.access(directory, os.R_OK)
            permissions["writable"] = os.access(directory, os.W_OK)
            permissions["executable"] = os.access(directory, os.X_OK)
        
        return permissions
    
    def create_directory_safely(self, directory: str) -> Dict[str, Any]:
        """Create directory with proper error handling and permission checks
        
        Args:
            directory: Directory path to create
            
        Returns:
            Dict with operation status
        """
        result = {
            "success": False,
            "message": "",
            "permissions": {}
        }
        
        try:
            # Check if parent directory exists and is writable
            parent_dir = os.path.dirname(directory)
            if parent_dir and not os.path.exists(parent_dir):
                parent_result = self.create_directory_safely(parent_dir)
                if not parent_result["success"]:
                    result["message"] = f"Failed to create parent directory: {parent_result['message']}"
                    return result
            
            # Create the directory if it doesn't exist
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                result["message"] = f"Created directory: {directory}"
            else:
                result["message"] = f"Directory already exists: {directory}"
            
            # Check permissions after creation
            result["permissions"] = self.check_directory_permissions(directory)
            result["success"] = result["permissions"]["writable"]
            
            if not result["success"]:
                result["message"] = f"Directory not writable: {directory}"
            
        except PermissionError as e:
            result["message"] = f"Permission error: {str(e)}"
        except OSError as e:
            result["message"] = f"OS error: {str(e)}"
        except Exception as e:
            result["message"] = f"Unexpected error: {str(e)}"
        
        return result
    
    def _create_agent(self, agent_config, tools):
        """Create an agent with the specified configuration and tools"""
        # Determine if this agent should have delegation capability
        # Project Manager and Software Architect should always have delegation
        is_leader = agent_config.get("name") in ["Project Manager", "Software Architect"]
        allow_delegation = agent_config.get("allow_delegation", False) or is_leader
        
        # Determine appropriate memory settings - always enable for complex tasks
        memory_enabled = agent_config.get("memory", True)
        
        # Get code execution settings from config or use defaults
        allow_code_execution = agent_config.get("allow_code_execution", False)
        code_execution_mode = agent_config.get("code_execution_mode", "safe")
        max_retry_limit = agent_config.get("max_retry_limit", 3)
        
        # Set max iterations based on role complexity
        if agent_config.get("name") == "Project Manager":
            max_iter = 30  # More iterations for complex planning
        elif agent_config.get("name") in ["Software Architect", "Fullstack Developer"]:
            max_iter = 25  # Medium iterations for development
        else:
            max_iter = 20  # Standard iterations for other roles
        
        # Use a separate copy of llm_config for each agent to avoid shared state
        agent_llm_config = {
            "model": "openai/gpt-4",
            "temperature": agent_config.get("temperature", 0.7)
        }
        
        # Check if the tool has the same name as the CodeInterpreterTool
        has_code_interpreter = any(getattr(tool, 'name', '') == 'Code Interpreter' for tool in tools)
        
        # Create the agent with enhanced attributes
        agent = Agent(
            name=agent_config["name"],
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            verbose=agent_config.get("verbose", True),
            allow_delegation=allow_delegation,
            temperature=agent_config.get("temperature", 0.7),
            memory=memory_enabled,
            tools=tools,
            llm_config=agent_llm_config,  # Use agent-specific LLM config
            max_iter=max_iter,  # Set iterations based on role
            # Only set allow_code_execution if CodeInterpreterTool is not in tools
            # (to avoid duplicate code execution capabilities)
            allow_code_execution=allow_code_execution and not has_code_interpreter,
            code_execution_mode=code_execution_mode,
            respect_context_window=True,  # Prevent context window issues
            max_retry_limit=max_retry_limit  # Use config value or default
        )
        
        return agent
        
    def get_project_manager_agent(self):
        """Get the Project Manager agent for direct communication"""
        # Load agent configurations
        agents_config = self._load_config("agents.yaml")
        
        # Create the Project Manager agent with all tools
        tools = [
            # Project Manager specific tools
            RequirementsAnalysisTool(),
            TaskTrackingTool(),
            AgileProjectManagementTool(),
            # Generic CrewAI tools
            brave_search_tool,
            directory_read_tool,
            file_read_tool,
            file_writer_tool,
            github_search_tool
        ]
        
        # Create agent
        agent = self._create_agent(agents_config["project_manager"], tools)
        
        # We'll use a direct implementation rather than monkey patching
        class ProjectManagerAgent:
            def __init__(self, agent):
                self.agent = agent
                
            def process_direct_message(self, messages, codebase_dir):
                """Process a direct message from the user to the Project Manager agent"""
                # Build the context from the messages
                message_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
                
                # Form a prompt for the agent
                prompt = f"""You are the Project Manager for a software development team.
                
The user is asking for your help with a codebase located at: {codebase_dir}

Chat history:
{message_history}

You have the following tools available:
- Requirements analysis
- Task tracking
- Project management
- Web search
- File and directory operations

Analyze the user's request and provide a helpful, concise response. If the user asks about code or files, 
use your tools to examine the codebase first. If the user asks for research, use the web search tool.
                """
                
                # In a production implementation, we would properly use the agent's process method
                # to generate a real response using LLM through the agent
                try:
                    # Access the LLM directly through the agent
                    response = self.agent.llm.invoke(prompt)
                    return response
                except Exception as e:
                    # Fallback response in case of any errors
                    print(f"Error in agent processing: {str(e)}")
                    return f"I'm analyzing your question about {messages[-1]['content']}. I'll examine the codebase at {codebase_dir} to provide relevant information."
                
        # Create the wrapper
        pm_agent = ProjectManagerAgent(agent)
        
        return pm_agent
        
    def set_model(self, model_name: str):
        """Set a specific model to use"""
        self.current_model = model_name
        
    def reset_memories(self, memory_type="all"):
        """Reset memories for agents"""
        # This would need to be implemented in a real application
        # to reset agent memories as needed
        if memory_type == "all":
            print(f"All memories reset.")
        else:
            print(f"Reset {memory_type} memories.")
        
    def backup_file(self, file_path: str) -> Dict[str, Any]:
        """Create a backup of a file before modifying it
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Dict with backup information
        """
        result = {
            "success": False,
            "backup_path": None,
            "message": ""
        }
        
        if not os.path.exists(file_path):
            result["message"] = f"File does not exist: {file_path}"
            return result
        
        try:
            # Create backups directory
            backup_dir = os.path.join(os.path.dirname(file_path), ".backups")
            dir_result = self.create_directory_safely(backup_dir)
            if not dir_result["success"]:
                result["message"] = f"Failed to create backup directory: {dir_result['message']}"
                return result
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, f"{base_name}.{timestamp}.bak")
            
            # Copy file
            import shutil
            shutil.copy2(file_path, backup_path)
            
            result["success"] = True
            result["backup_path"] = backup_path
            result["message"] = f"Backup created at: {backup_path}"
            
        except Exception as e:
            result["message"] = f"Failed to create backup: {str(e)}"
        
        return result
    
    def run(self, project_goal: str, codebase_dir: str, non_interactive: bool = False, training_mode: bool = False) -> Dict[str, Any]:
        """Run the development crew with enhanced collaboration and task management
        
        Args:
            project_goal: The goal of the project
            codebase_dir: The directory where to store code
            non_interactive: If True, don't prompt for user input during execution
            training_mode: If True, enables training-specific behaviors
        """
        self.project_goal = project_goal
        self.codebase_dir = codebase_dir
        self.non_interactive = non_interactive
        self.training_mode = training_mode
        
        # Reset token usage for this run
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        
        # Create codebase directory if it doesn't exist with proper error handling
        dir_result = self.create_directory_safely(codebase_dir)
        if not dir_result["success"]:
            print(f"Warning: {dir_result['message']}")
            if not dir_result["permissions"].get("exists", False):
                print(f"Will attempt to continue without the directory, but some operations may fail.")
        else:
            # Add a README.md file to help the agents
            readme_path = os.path.join(codebase_dir, "README.md")
            if not os.path.exists(readme_path):
                try:
                    with open(readme_path, "w") as f:
                        f.write(f"# {project_goal}\n\nThis project is managed by the Dev Team crew.\n")
                except Exception as e:
                    print(f"Warning: Could not create README file: {str(e)}")
        
        # Set up the output directory structure
        self.setup_output_directory()
        
        # Log start of execution
        print(f"Starting Dev Team Crew with project goal: {project_goal}")
        print(f"Working in directory: {codebase_dir}")
        print(f"Sprint {self.sprint_number} beginning...")
        
        # Get agents in the correct hierarchical order with proper leadership
        ordered_agent_ids = self.get_hierarchical_agent_order()
        ordered_agents = [self.get_agents()[agent_id] for agent_id in ordered_agent_ids if agent_id in self.get_agents()]
        
        if not ordered_agents:
            raise ValueError("No agents available to run the crew. Check agent configuration.")
        
        # Log agent roles and hierarchy
        print("\nAgent Team Structure:")
        print("=====================")
        for i, agent_id in enumerate(ordered_agent_ids):
            if agent_id in self.get_agents():
                agent = self.get_agents()[agent_id]
                leadership = "LEADER" if i == 0 else ""
                # Access configuration attributes directly as agent attributes may not be accessible
                agent_name = self.agents_config[agent_id]["name"]
                agent_role = self.agents_config[agent_id]["role"]
                print(f"{i+1}. {agent_name} ({agent_role}) {leadership}")
        print("=====================\n")
        
        # Create the crew with initial tasks
        tasks = self.get_tasks(project_goal, codebase_dir)
        
        if not tasks:
            raise ValueError("No tasks defined. Check task configuration.")
        
        # Log tasks and dependencies
        print("\nTask Sequence:")
        print("=============")
        for i, task in enumerate(tasks):
            # Get the task ID from our map if available
            self.task_id_map = getattr(self, 'task_id_map', {})
            task_id = self.task_id_map.get(id(task), f"Task-{i+1}")
            
            # Get first line of description safely
            try:
                if isinstance(task.description, str) and task.description.strip():
                    first_line = task.description.splitlines()[0][:50]
                else:
                    first_line = "Task description not available"
            except (AttributeError, IndexError):
                first_line = "Task description not available"
                
            # Get dependency count safely
            try:
                dep_count = len(task.context) if hasattr(task, 'context') and task.context else 0
                dep_status = f"with {dep_count} dependencies" if dep_count > 0 else "no dependencies"
            except:
                dep_status = "dependency info not available"
                
            print(f"{i+1}. {task_id}: {first_line}... ({dep_status})")
        print("=============\n")
        
        # Configure the embedder for memory
        embedder_config = {
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small"
            }
        }
        
        # Create crew inputs with non_interactive flag if needed
        crew_inputs = {
            "project_goal": project_goal,
            "codebase_dir": codebase_dir,
            "sprint_number": self.sprint_number,
            "team_structure": {agent_id: self.agents_config[agent_id]["role"] for agent_id in ordered_agent_ids if agent_id in self.agents_config},
            "workflow": "hierarchical",
            "working_directory": os.getcwd()
        }
        
        # Add non_interactive flag to inputs if specified
        if hasattr(self, 'non_interactive') and self.non_interactive:
            crew_inputs["non_interactive"] = True
            crew_inputs["auto_reply_to_human_input"] = "Continue with the implementation using best practices."
        
        # Create the crew with a hierarchical process, planning and memory capabilities
        self.active_crew = Crew(
            agents=ordered_agents,
            tasks=tasks,
            process=Process.hierarchical,  # Use hierarchical process for better collaboration
            verbose=True,
            manager_llm=self.llm_config["model"],  # Use the same LLM as agents
            planning=True,  # Enable planning before task execution
            planning_llm=self.llm_config["model"],  # Use the same LLM for planning
            memory=True,  # Enable memory for storing execution history
            embedder=embedder_config,  # Configure embedder for memory
            # Pass rich initial context for all agents
            inputs=crew_inputs
        )
        
        # Create a reference to the current crew for easier access
        crew = self.active_crew
        
        # Run the crew with proper error handling, recovery, and timeout management
        import signal
        import threading
        import time
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Crew execution timed out")
        
        def run_with_timeout(timeout_seconds=600, max_retries=3):
            result_container = {"result": None, "error": None, "retries": 0}
            
            def run_crew_task():
                try:
                    result_container["result"] = crew.kickoff()
                except Exception as e:
                    result_container["error"] = str(e)
            
            # Try up to max_retries times with exponential backoff
            for retry in range(max_retries):
                # Clear previous results
                result_container["result"] = None
                result_container["error"] = None
                
                # Create and start thread
                thread = threading.Thread(target=run_crew_task)
                thread.daemon = True
                thread.start()
                
                # Wait for completion with timeout
                thread.join(timeout_seconds)
                
                # Check results
                if thread.is_alive():
                    print(f"Execution timed out (retry {retry+1}/{max_retries})")
                    # If we've retried max times, return timeout error
                    if retry == max_retries - 1:
                        return None, "Final execution timed out"
                    
                    # Otherwise, kill thread and retry after backoff
                    # Note: This is a soft kill, thread may continue running
                    timeout_seconds *= 1.5  # Increase timeout for next retry
                    time.sleep(2 * (retry + 1))  # Exponential backoff
                    continue
                
                # If no error, return result
                if not result_container["error"]:
                    if retry > 0:
                        print(f"Succeeded after {retry+1} attempts")
                    return result_container["result"], None
                
                # If error is rate limit or token related, retry
                error_lower = result_container["error"].lower()
                if any(term in error_lower for term in ["rate limit", "token", "timeout", "too many requests"]):
                    print(f"Recoverable error (retry {retry+1}/{max_retries}): {result_container['error']}")
                    
                    # If this was the last retry, return the error
                    if retry == max_retries - 1:
                        return None, result_container["error"]
                    
                    # Calculate backoff time based on retry count (exponential backoff)
                    backoff_time = 5 * (2 ** retry)  # 5, 10, 20, 40, 80, etc. seconds
                    print(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                    continue
                
                # For non-recoverable errors, return immediately
                return None, result_container["error"]
            
            # Should never reach here, but just in case
            return None, "Max retries exceeded"
        
        # Execute sprint with checkpointing
        try:
            print(f"\nExecuting Sprint {self.sprint_number}...")
            
            # Create checkpoint file
            checkpoint_file = os.path.join(
                self.codebase_dir, "results", f"sprint_{self.sprint_number}", "checkpoint.json"
            )
            
            # Save checkpoint state
            try:
                checkpoint_data = {
                    "sprint": self.sprint_number,
                    "timestamp": datetime.now().isoformat(),
                    "project_goal": self.project_goal,
                    "status": "starting"
                }
                os.makedirs(os.path.dirname(checkpoint_file), exist_ok=True)
                with open(checkpoint_file, "w") as f:
                    json.dump(checkpoint_data, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not create checkpoint file: {str(e)}")
            
            # Run with a timeout and retry mechanism
            result, error = run_with_timeout(timeout_seconds=600, max_retries=3)
            
            if error:
                print(f"Error during crew execution: {error}")
                # Create minimal result data on error
                result = {
                    "error": error,
                    "status": "failed",
                    "sprint": self.sprint_number,
                    "token_usage": self.token_usage
                }
                
                # Update checkpoint with failure status
                try:
                    checkpoint_data["status"] = "failed"
                    checkpoint_data["error"] = error
                    checkpoint_data["completed_at"] = datetime.now().isoformat()
                    with open(checkpoint_file, "w") as f:
                        json.dump(checkpoint_data, f, indent=2)
                except Exception as e:
                    print(f"Warning: Could not update checkpoint file: {str(e)}")
            else:
                print(f"Sprint {self.sprint_number} completed successfully!")
                
                # Update checkpoint with success status
                try:
                    checkpoint_data["status"] = "completed"
                    checkpoint_data["completed_at"] = datetime.now().isoformat()
                    with open(checkpoint_file, "w") as f:
                        json.dump(checkpoint_data, f, indent=2)
                except Exception as e:
                    print(f"Warning: Could not update checkpoint file: {str(e)}")
                    
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error during crew execution: {str(e)}")
            print(f"Error details: {error_details}")
            
            # Create minimal result data on error
            result = {
                "error": str(e),
                "error_details": error_details,
                "status": "failed",
                "sprint": self.sprint_number,
                "token_usage": self.token_usage
            }
            
            # Still save the error result but continue processing
        
        # Save the results for this sprint
        results_file = os.path.join(self.codebase_dir, "results", f"sprint_{self.sprint_number}", "result.json")
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, "w") as f:
            import json
            json.dump(result, f, indent=2)
        
        # Create a sprint summary with task outputs
        self._create_sprint_summary(result)
        
        # Collect user feedback after the sprint
        self.collect_user_feedback(non_interactive=getattr(self, 'non_interactive', False))
        
        # If feedback was provided, increment sprint number and run another cycle with the feedback
        if self.user_feedback:
            print(f"\nInitiating Sprint {self.sprint_number + 1} based on feedback...")
            self.sprint_number += 1
            
            # Set up the output directory for the next sprint
            self.setup_output_directory()
            
            # Update tasks with feedback for the next sprint
            tasks = self.get_tasks(project_goal, codebase_dir)
            
            # Configure the embedder for memory
            embedder_config = {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
            
            # Create crew inputs with non_interactive flag if needed
            crew_inputs = {
                "project_goal": project_goal,
                "codebase_dir": codebase_dir,
                "sprint_number": self.sprint_number,
                "previous_feedback": self.user_feedback,
                "previous_sprint_results": result,
                "team_structure": {agent_id: self.agents_config[agent_id]["role"] for agent_id in ordered_agent_ids if agent_id in self.agents_config},
                "workflow": "hierarchical",
                "working_directory": os.getcwd()
            }
            
            # Add non_interactive flag to inputs if specified
            if hasattr(self, 'non_interactive') and self.non_interactive:
                crew_inputs["non_interactive"] = True
                crew_inputs["auto_reply_to_human_input"] = "Continue with the implementation using best practices."
            
            # Create a new crew for the next sprint with enhanced context, planning and memory
            self.active_crew = Crew(
                agents=ordered_agents,
                tasks=tasks,
                process=Process.hierarchical,
                verbose=True,
                manager_llm=self.llm_config["model"],
                planning=True,  # Enable planning before task execution
                planning_llm=self.llm_config["model"],  # Use the same LLM for planning
                memory=True,  # Enable memory for storing execution history
                embedder=embedder_config,  # Configure embedder for memory
                inputs=crew_inputs
            )
            
            # Create a reference to the current crew for easier access
            crew = self.active_crew
            
            # Run the crew again for the next sprint
            try:
                next_result = crew.kickoff()
                print(f"Sprint {self.sprint_number} completed successfully!")
                
                # Save the results for this sprint
                results_file = os.path.join(self.codebase_dir, "results", f"sprint_{self.sprint_number}", "result.json")
                with open(results_file, "w") as f:
                    import json
                    json.dump(next_result, f, indent=2)
                
                # Create a sprint summary for the next sprint
                self._create_sprint_summary(next_result)
                
                # Update the result for the return value
                result = next_result
            except Exception as e:
                print(f"Error during next sprint execution: {str(e)}")
                # Don't update the result value, just keep the previous successful one
        
        print("\nDev Team execution completed successfully!")
        return result
        
    def reset_memories(self, memory_type: str = 'all') -> None:
        """Reset specified memory types for the crew
        
        Args:
            memory_type: Type of memory to reset. Options are:
                - 'long': Reset long-term memory
                - 'short': Reset short-term memory
                - 'entities': Reset entity memory
                - 'kickoff_outputs': Reset latest kickoff task outputs
                - 'knowledge': Reset knowledge storage
                - 'all': Reset all memories
        """
        try:
            # First try to use the Crew object method if we have an active crew
            if hasattr(self, 'active_crew') and self.active_crew:
                # Map memory_type to command_type for Crew.reset_memories
                command_type_map = {
                    'long': 'long',
                    'short': 'short',
                    'entities': 'entities',
                    'kickoff_outputs': 'kickoff_outputs',
                    'knowledge': 'knowledge',
                    'all': 'all'
                }
                command_type = command_type_map.get(memory_type, 'all')
                self.active_crew.reset_memories(command_type=command_type)
                print(f"Successfully reset {memory_type} memories using crew object")
                return
                
            # Fallback to CLI command if no active crew
            import subprocess
            
            # Map memory_type to CLI flag
            flag_map = {
                'long': '-l',
                'short': '-s',
                'entities': '-e',
                'kickoff_outputs': '-k',
                'knowledge': '-kn',
                'all': '-a'
            }
            
            # Get the appropriate flag
            flag = flag_map.get(memory_type, '-a')  # Default to '-a' if invalid type
            
            # Run the crewai CLI command to reset memories
            subprocess.run(['crewai', 'reset-memories', flag], check=True)
            
            print(f"Successfully reset {memory_type} memories using CLI")
        except Exception as e:
            print(f"Error resetting memories: {str(e)}")
    
    def _create_sprint_summary(self, result: Dict[str, Any]) -> None:
        """Create a human-readable summary of the sprint results"""
        try:
            summary_file = os.path.join(self.codebase_dir, "results", f"sprint_{self.sprint_number}", "summary.md")
            os.makedirs(os.path.dirname(summary_file), exist_ok=True)
            
            with open(summary_file, "w") as f:
                f.write(f"# Sprint {self.sprint_number} Summary\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(f"**Project Goal:** {self.project_goal}\n")
                f.write(f"**Codebase Directory:** {self.codebase_dir}\n\n")
                
                f.write("## Completed Tasks\n\n")
                
                # Try to extract task information from various result formats
                tasks_info = []
                
                # Format 1: Dictionary with 'tasks' key
                if isinstance(result, dict) and "tasks" in result and isinstance(result["tasks"], list):
                    tasks_info = result["tasks"]
                
                # Format 2: List directly
                elif isinstance(result, list):
                    tasks_info = result
                    
                # Format 3: Dictionary with raw text
                elif isinstance(result, dict) and "raw" in result:
                    f.write(f"**Result:** {result['raw']}\n\n")
                
                # Format 4: String directly
                elif isinstance(result, str):
                    f.write(f"**Result:** {result}\n\n")
                
                # Process task information if available
                if tasks_info:
                    for i, task in enumerate(tasks_info):
                        if isinstance(task, dict):
                            task_name = task.get('name', f'Task {i+1}')
                            task_agent = task.get('agent', 'Unknown')
                            task_status = task.get('status', 'Completed')
                            
                            f.write(f"### {i+1}. {task_name}\n")
                            f.write(f"**Agent:** {task_agent}\n")
                            f.write(f"**Status:** {task_status}\n")
                            f.write("\n")
                        elif hasattr(task, 'description'):
                            # It might be a Task object
                            f.write(f"### {i+1}. Task\n")
                            try:
                                f.write(f"**Description:** {str(task.description)[:100]}...\n")
                            except:
                                f.write(f"**Description:** Unable to access task description\n")
                            f.write("\n")
                else:
                    f.write("No detailed task information available.\n\n")
                
                f.write("## User Feedback\n\n")
                if self.user_feedback:
                    f.write(f"{self.user_feedback}\n\n")
                else:
                    f.write("No user feedback provided for this sprint.\n\n")
                
                f.write("## Next Steps\n\n")
                f.write("1. Review the implemented features and code quality\n")
                f.write("2. Incorporate feedback into the next sprint planning\n")
                f.write("3. Refine the requirements based on current progress\n")
                
            print(f"Sprint summary created at: {summary_file}")
        except Exception as e:
            print(f"Warning: Failed to create sprint summary: {str(e)}")

    def train(self, n_iterations: int, inputs: Dict[str, Any] = None, filename: str = None) -> Dict[str, Any]:
        """Train the crew for a specific number of iterations
        
        Args:
            n_iterations: Number of training iterations
            inputs: Dictionary of inputs for the training
            filename: Optional filename to save model to (.pkl file)
            
        Returns:
            Training results
        """
        # Validate inputs
        if n_iterations <= 0:
            raise ValueError("Number of iterations must be positive")
        
        if filename and not filename.endswith(".pkl"):
            raise ValueError("Filename must end with .pkl")
        
        # Use default inputs if none provided
        inputs = inputs or {}
        project_goal = inputs.get("project_goal", self.project_goal) or "Create a simple application"
        codebase_dir = inputs.get("codebase_dir", self.codebase_dir) or "./training_project"
        
        print(f"Starting training for {n_iterations} iterations")
        print(f"Project Goal: {project_goal}")
        print(f"Codebase Directory: {codebase_dir}")
        
        # Initialize training stats
        training_stats = {
            "iterations": n_iterations,
            "results": [],
            "token_usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            },
            "agent_parameters": {},
            "feedback_analysis": {}
        }
        
        # Initial agent parameters
        for agent_id, config in self.agents_config.items():
            training_stats["agent_parameters"][agent_id] = {
                "temperature": config.get("temperature", 0.7),
                "verbosity": config.get("verbose", True),
                "max_iter": 20,  # Default value
                "model": self.available_models["medium"]  # Default model
            }
        
        # Run training iterations
        for i in range(n_iterations):
            print(f"\n{'='*30} TRAINING ITERATION {i+1}/{n_iterations} {'='*30}")
            
            # Run with training mode enabled
            result = self.run(project_goal, codebase_dir, non_interactive=False, training_mode=True)
            
            # Get human feedback for this iteration
            feedback = self.collect_user_feedback(non_interactive=False)
            
            # Analyze feedback and adjust agent parameters
            self._incorporate_feedback(feedback)
            
            # Store iteration results
            iteration_result = {
                "iteration": i + 1,
                "feedback": feedback,
                "agent_parameters": {},
                "token_usage": self.token_usage.copy()
            }
            
            # Record current agent parameters
            for agent_id, config in self.agents_config.items():
                iteration_result["agent_parameters"][agent_id] = {
                    "temperature": config.get("temperature", 0.7),
                    "verbosity": config.get("verbose", True)
                }
            
            # Update overall token usage
            training_stats["token_usage"]["prompt_tokens"] += self.token_usage["prompt_tokens"]
            training_stats["token_usage"]["completion_tokens"] += self.token_usage["completion_tokens"]
            training_stats["token_usage"]["total_tokens"] += self.token_usage["total_tokens"]
            
            # Add to results
            training_stats["results"].append(iteration_result)
            
            # Print summary of this iteration
            print(f"\nIteration {i+1} summary:")
            print(f"Token usage: {self.token_usage}")
            print(f"Feedback: {feedback}")
            
            # Wait before next iteration
            if i < n_iterations - 1:
                print("\nPreparing for next iteration...")
                import time
                time.sleep(2)  # Brief pause between iterations
        
        # Save model if filename provided
        if filename:
            self._save_trained_model(filename, training_stats)
            print(f"\nTraining model saved to {filename}")
        
        print("\nTraining completed successfully!")
        return training_stats
    
    def _incorporate_feedback(self, feedback: str) -> Dict[str, Any]:
        """Analyze feedback and adjust agent parameters
        
        Args:
            feedback: User feedback string
            
        Returns:
            Dict with feedback analysis and adjustments made
        """
        adjustments = {
            "temperature_changes": {},
            "verbosity_changes": {},
            "model_changes": {},
            "feedback_categories": set()
        }
        
        feedback_lower = feedback.lower()
        
        # Check for verbosity feedback
        if any(term in feedback_lower for term in ["too verbose", "less detail", "too much detail"]):
            adjustments["feedback_categories"].add("verbosity_reduction")
            
            # Reduce verbosity for all agents
            for agent_id in self.agents_config:
                if self.agents_config[agent_id].get("verbose", True):
                    self.agents_config[agent_id]["verbose"] = False
                    adjustments["verbosity_changes"][agent_id] = True, False
        
        elif any(term in feedback_lower for term in ["more detail", "more verbose", "need more information"]):
            adjustments["feedback_categories"].add("verbosity_increase")
            
            # Increase verbosity for all agents
            for agent_id in self.agents_config:
                if not self.agents_config[agent_id].get("verbose", True):
                    self.agents_config[agent_id]["verbose"] = True
                    adjustments["verbosity_changes"][agent_id] = False, True
        
        # Check for creativity feedback
        if any(term in feedback_lower for term in ["more creative", "too rigid", "too strict", "more variety"]):
            adjustments["feedback_categories"].add("creativity_increase")
            
            # Increase temperature for all agents
            for agent_id in self.agents_config:
                old_temp = self.agents_config[agent_id].get("temperature", 0.7)
                new_temp = min(1.0, old_temp + 0.1)  # Cap at 1.0
                self.agents_config[agent_id]["temperature"] = new_temp
                adjustments["temperature_changes"][agent_id] = old_temp, new_temp
                
        elif any(term in feedback_lower for term in ["less creative", "too random", "more focused", "more consistent"]):
            adjustments["feedback_categories"].add("creativity_reduction")
            
            # Decrease temperature for all agents
            for agent_id in self.agents_config:
                old_temp = self.agents_config[agent_id].get("temperature", 0.7)
                new_temp = max(0.1, old_temp - 0.1)  # Minimum 0.1
                self.agents_config[agent_id]["temperature"] = new_temp
                adjustments["temperature_changes"][agent_id] = old_temp, new_temp
        
        # Check for model quality feedback
        if any(term in feedback_lower for term in ["better quality", "smarter", "more intelligent", "improve quality"]):
            adjustments["feedback_categories"].add("model_quality_increase")
            
            # Upgrade models for specific roles mentioned, or all if none specified
            leadership_roles = ["project_manager", "software_architect"]
            
            for agent_id in leadership_roles:
                if agent_id in self.agents_config:
                    self.agents_config[agent_id]["model"] = self.available_models["large"]
                    adjustments["model_changes"][agent_id] = "upgraded to large model"
        
        # Check for efficiency feedback
        if any(term in feedback_lower for term in ["faster", "too slow", "speed up", "more efficient"]):
            adjustments["feedback_categories"].add("efficiency_increase")
            
            # Use smaller models for simple tasks
            implementation_roles = ["fullstack_developer", "test_engineer"]
            
            for agent_id in implementation_roles:
                if agent_id in self.agents_config and "simple" in feedback_lower:
                    self.agents_config[agent_id]["model"] = self.available_models["small"]
                    adjustments["model_changes"][agent_id] = "downgraded to small model for efficiency"
        
        # Convert set to list for JSON serialization
        adjustments["feedback_categories"] = list(adjustments["feedback_categories"])
        
        # Log adjustments
        if adjustments["temperature_changes"] or adjustments["verbosity_changes"] or adjustments["model_changes"]:
            print("\nAdjusting agent parameters based on feedback:")
            
            if adjustments["temperature_changes"]:
                print("Temperature changes:")
                for agent_id, (old, new) in adjustments["temperature_changes"].items():
                    print(f"  - {agent_id}: {old:.1f} → {new:.1f}")
            
            if adjustments["verbosity_changes"]:
                print("Verbosity changes:")
                for agent_id, (old, new) in adjustments["verbosity_changes"].items():
                    print(f"  - {agent_id}: {old} → {new}")
            
            if adjustments["model_changes"]:
                print("Model changes:")
                for agent_id, change in adjustments["model_changes"].items():
                    print(f"  - {agent_id}: {change}")
        else:
            print("\nNo parameter adjustments needed based on feedback.")
        
        return adjustments
    
    def _save_trained_model(self, filename: str, training_stats: Dict[str, Any]) -> None:
        """Save the trained model and stats to a file
        
        Args:
            filename: Name of the file to save to
            training_stats: Training statistics to save
        """
        import pickle
        
        # Prepare data to save
        model_data = {
            "agents_config": self.agents_config,
            "training_stats": training_stats,
            "timestamp": datetime.now().isoformat(),
            "project_goal": self.project_goal,
            "codebase_dir": self.codebase_dir
        }
        
        try:
            with open(filename, 'wb') as f:
                pickle.dump(model_data, f)
        except Exception as e:
            print(f"Error saving model: {str(e)}")
    
    def load_trained_model(self, filename: str) -> Dict[str, Any]:
        """Load a trained model from a file
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            Loaded model data
        """
        import pickle
        
        try:
            with open(filename, 'rb') as f:
                model_data = pickle.load(f)
            
            # Update agent configurations
            self.agents_config = model_data.get("agents_config", self.agents_config)
            
            # Log loaded model information
            print(f"Loaded trained model from {filename}")
            print(f"Training timestamp: {model_data.get('timestamp')}")
            print(f"Number of training iterations: {len(model_data.get('training_stats', {}).get('results', []))}")
            
            return model_data
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return {}
