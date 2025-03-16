#!/usr/bin/env python3
"""
Dev Team Crew - Implementation of the Dev Team using CrewAI.
This module provides the DevTeamCrew class for orchestrating the development team agents.
"""

import os
import sys
import json
import logging
import yaml
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

from crewai import Crew, Agent, Task, Process
from crewai.tasks.task_output import TaskOutput

# Try to import AgentCache from different possible locations
try:
    from crewai.agents.cache import AgentCache
except ImportError:
    try:
        from crewai.utilities import AgentCache
    except ImportError:
        # If not available, create a simple cache class
        class AgentCache:
            def __init__(self):
                self.cache = {}
            
            def reset(self, memory_type=None):
                if memory_type is None or memory_type == "all":
                    self.cache = {}
                else:
                    if memory_type in self.cache:
                        del self.cache[memory_type]

# Import custom tools
from .tools.dev_tools import TOOLS_MAP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("dev_team_crew")

class DevTeamCrew:
    """
    Development Team Crew using CrewAI with specialized agents for software development.
    Implements a hierarchical team structure with Project Manager, Software Architect,
    Fullstack Developer, and Test Engineer roles.
    """
    
    def __init__(
        self,
        project_goal: str,
        codebase_dir: str,
        interactive: bool = True,
        training_mode: bool = False,
        test_mode: bool = False,
        replay_mode: bool = False,
        reset_mode: bool = False,
        chat_mode: bool = False,
        model: str = "gpt-4",
        process_type = None,
        memory_enabled: bool = True,
        tools_list: List[str] = None,
        verbose: bool = True,
        allow_delegation: bool = True
    ):
        """
        Initialize the Dev Team Crew with enhanced CrewAI options.
        
        Args:
            project_goal (str): The goal of the project
            codebase_dir (str): The directory containing the codebase
            interactive (bool, optional): Whether to run in interactive mode. Defaults to True.
            training_mode (bool, optional): Whether to run in training mode. Defaults to False.
            test_mode (bool, optional): Whether to run in test mode. Defaults to False.
            replay_mode (bool, optional): Whether to run in replay mode. Defaults to False.
            reset_mode (bool, optional): Whether to run in reset mode. Defaults to False.
            chat_mode (bool, optional): Whether to run in chat mode. Defaults to False.
            model (str, optional): The model to use. Defaults to "gpt-4".
            process_type (Process, optional): The CrewAI process type. Defaults to Process.hierarchical.
            memory_enabled (bool, optional): Whether to enable agent memory. Defaults to True.
            tools_list (List[str], optional): List of tool names to enable. Defaults to None (all tools).
            verbose (bool, optional): Whether to enable verbose output. Defaults to True.
            allow_delegation (bool, optional): Whether to enable agent delegation. Defaults to True.
        """
        self.project_goal = project_goal
        self.codebase_dir = os.path.abspath(codebase_dir)
        self.interactive = interactive
        self.training_mode = training_mode
        self.test_mode = test_mode
        self.replay_mode = replay_mode
        self.reset_mode = reset_mode
        self.chat_mode = chat_mode
        self.model = model
        
        # Store enhanced CrewAI options
        from crewai import Process
        self.process_type = process_type if process_type else Process.hierarchical
        self.memory_enabled = memory_enabled
        
        # Handle tools_list which can be a comma-separated string from terminal_client
        if isinstance(tools_list, str) and tools_list != "all":
            self.tools_list = [tool.strip() for tool in tools_list.split(",")]
            logger.info(f"Parsed tools list from string: {self.tools_list}")
        else:
            self.tools_list = tools_list
            
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        
        # Initialize crew components
        self.agents = {}
        self.tasks = {}
        self.crew = None
        self.sprint_counter = 1
        self.results_dir = os.path.join(self.codebase_dir, "results")
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Load agent and task configurations
        self._load_configurations()
        
        # Initialize crew and agents
        if not (self.reset_mode or self.chat_mode):
            self._initialize_crew()
    
    def _load_configurations(self):
        """Load agent and task configurations from YAML files"""
        # Define default config paths
        config_dir = os.path.join(os.path.dirname(__file__), "config")
        agents_config_path = os.path.join(config_dir, "agents.yaml")
        tasks_config_path = os.path.join(config_dir, "tasks.yaml")
        
        # Create default configs if they don't exist
        self._create_default_configs(config_dir, agents_config_path, tasks_config_path)
        
        # Load configurations
        try:
            with open(agents_config_path, 'r') as f:
                self.agents_config = yaml.safe_load(f)
            
            with open(tasks_config_path, 'r') as f:
                self.tasks_config = yaml.safe_load(f)
                
            logger.info("Configuration files loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configuration files: {str(e)}")
            # Use default configurations
            self.agents_config = self._get_default_agents_config()
            self.tasks_config = self._get_default_tasks_config()
            logger.info("Using default configurations")
    
    def _create_default_configs(self, config_dir, agents_config_path, tasks_config_path):
        """Create default configuration files if they don't exist"""
        os.makedirs(config_dir, exist_ok=True)
        
        # Create agents.yaml if it doesn't exist
        if not os.path.exists(agents_config_path):
            with open(agents_config_path, 'w') as f:
                yaml.dump(self._get_default_agents_config(), f, default_flow_style=False)
            logger.info(f"Created default agents configuration at {agents_config_path}")
        
        # Create tasks.yaml if it doesn't exist
        if not os.path.exists(tasks_config_path):
            with open(tasks_config_path, 'w') as f:
                yaml.dump(self._get_default_tasks_config(), f, default_flow_style=False)
            logger.info(f"Created default tasks configuration at {tasks_config_path}")
    
    def _get_default_agents_config(self):
        """Get default agent configurations"""
        return {
            "project_manager": {
                "role": "Project Manager",
                "goal": "Analyze requirements, create sprint plans, coordinate team, and ensure project success",
                "backstory": "You are a seasoned Project Manager with expertise in Agile methodologies and software development. You excel at analyzing requirements, breaking projects into manageable tasks, and coordinating diverse teams to deliver successful projects. You prioritize clarity in communication and efficient resource allocation.",
                "verbose": True,
                "tools": ["RequirementsAnalysisTool", "TaskTrackingTool", "AgileProjectManagementTool"]
            },
            "software_architect": {
                "role": "Software Architect",
                "goal": "Design system architecture, analyze code structure, recommend improvements, and ensure maintainable code",
                "backstory": "You are an experienced Software Architect with a deep understanding of software design patterns, architectural principles, and coding best practices. You excel at analyzing requirements and designing robust, scalable solutions. You value maintainability, simplicity, and elegance in code design.",
                "verbose": True,
                "tools": ["CodeAnalysisTool", "CodebaseAnalysisTool", "CodeRefactoringTool", "ObsoleteCodeCleanupTool"]
            },
            "fullstack_developer": {
                "role": "Fullstack Developer",
                "goal": "Implement features, fix bugs, manage dependencies, and ensure code quality",
                "backstory": "You are a skilled Fullstack Developer proficient in both frontend and backend technologies. You excel at implementing features, fixing bugs, and translating architectural designs into efficient, clean code. You value code quality, documentation, and adherence to best practices.",
                "verbose": True,
                "tools": ["CodeImplementationTool", "CodeGenerationTool", "DependencyManagementTool"]
            },
            "test_engineer": {
                "role": "Test Engineer",
                "goal": "Create tests, ensure code coverage, perform code reviews, and maintain code quality",
                "backstory": "You are a detail-oriented Test Engineer with expertise in test automation, code coverage analysis, and quality assurance. You excel at identifying edge cases, ensuring thorough test coverage, and maintaining high standards through rigorous code reviews. You value reliability, robustness, and maintainability in code.",
                "verbose": True,
                "tools": ["TestGenerationTool", "TestRunnerTool", "CodeCoverageTool", "CodeReviewTool"]
            }
        }
    
    def _get_default_tasks_config(self):
        """Get default task configurations"""
        return {
            "requirements_analysis": {
                "description": "Analyze project requirements and create product backlog with user stories and acceptance criteria",
                "agent": "project_manager",
                "dependencies": []
            },
            "architecture_design": {
                "description": "Design system components, organization, and data flow based on requirements",
                "agent": "software_architect",
                "dependencies": ["requirements_analysis"]
            },
            "codebase_analysis": {
                "description": "Analyze existing code structure and identify improvements",
                "agent": "software_architect",
                "dependencies": ["architecture_design"]
            },
            "sprint_planning": {
                "description": "Create sprint plan with prioritized backlog items",
                "agent": "project_manager",
                "dependencies": ["requirements_analysis", "codebase_analysis"]
            },
            "feature_implementation": {
                "description": "Implement features according to sprint plan",
                "agent": "fullstack_developer",
                "dependencies": ["sprint_planning"]
            },
            "test_development": {
                "description": "Write tests for implemented features",
                "agent": "test_engineer",
                "dependencies": ["feature_implementation"]
            },
            "code_review": {
                "description": "Review code against quality standards",
                "agent": "test_engineer",
                "dependencies": ["feature_implementation", "test_development"]
            },
            "code_refactoring": {
                "description": "Improve code structure and reduce complexity",
                "agent": "software_architect",
                "dependencies": ["code_review"]
            },
            "code_cleanup": {
                "description": "Remove obsolete code and dependencies",
                "agent": "software_architect",
                "dependencies": ["code_refactoring"]
            },
            "documentation_update": {
                "description": "Update documentation to reflect changes",
                "agent": "project_manager",
                "dependencies": ["code_cleanup"]
            },
            "sprint_retrospective": {
                "description": "Analyze sprint outcomes and plan improvements",
                "agent": "project_manager",
                "dependencies": ["documentation_update"]
            }
        }
    
    def _initialize_crew(self):
        """Initialize the crew with agents and tasks using the provided CrewAI options"""
        try:
            # Initialize agents with enhanced configurations based on passed parameters
            self.agents = {}
            for agent_id, agent_config in self.agents_config.items():
                # Get agent tools based on tools_list parameter
                agent_tools = []
                for tool_name in agent_config.get("tools", []):
                    # Skip tools not in tools_list if it's specified
                    if self.tools_list is not None and tool_name not in self.tools_list:
                        continue
                        
                    # Add tool if it's in the TOOLS_MAP
                    if tool_name in TOOLS_MAP:
                        agent_tools.append(TOOLS_MAP[tool_name])
                
                # Create agent with parameters passed from terminal_client.py
                self.agents[agent_id] = Agent(
                    role=agent_config["role"],
                    goal=agent_config["goal"],
                    backstory=agent_config["backstory"],
                    verbose=self.verbose and agent_config.get("verbose", True),
                    tools=agent_tools,
                    allow_delegation=self.allow_delegation,  # Use parameter from constructor
                    memory=self.memory_enabled,  # Use parameter from constructor
                    llm=self.model,
                    max_rpm=30,  # Rate limiting to prevent API throttling
                    max_iterations=10,  # Prevent infinite loops
                    max_execution_time=1800,  # 30 minute timeout per agent action
                )
                
                logger.info(f"Initialized agent '{agent_id}' with {len(agent_tools)} tools")
                logger.info(f"  Allow Delegation: {self.allow_delegation}")
                logger.info(f"  Memory Enabled: {self.memory_enabled}")
                logger.info(f"  Verbose: {self.verbose}")
            
            # Initialize tasks with enhanced context
            self.tasks = {}
            for task_id, task_config in self.tasks_config.items():
                # Check if agent exists
                agent_id = task_config["agent"]
                if agent_id not in self.agents:
                    logger.warning(f"Agent '{agent_id}' not found for task '{task_id}'")
                    continue
                
                # Create task description with detailed context
                task_description = f"""
                Project Goal: {self.project_goal}
                Codebase Directory: {self.codebase_dir}
                Task: {task_config["description"]}
                
                Work on the codebase in {self.codebase_dir}.
                """
                
                # Create task with enhanced configuration
                task_context = {
                    "project_goal": self.project_goal,
                    "codebase_dir": self.codebase_dir,
                    "task_description": task_config["description"],
                    "agent_role": self.agents[agent_id].role,
                    "sprint": self.sprint_counter
                }
                
                # Add custom context from task config if available
                if "context" in task_config:
                    task_context.update(task_config["context"])
                
                # Create task with priority based on dependency chain
                priority = len(task_config.get("dependencies", []))
                
                # Create output directory path
                output_dir = os.path.join(self.results_dir, f"sprint_{self.sprint_counter}")
                os.makedirs(output_dir, exist_ok=True)
                
                self.tasks[task_id] = Task(
                    description=task_description,
                    agent=self.agents[agent_id],
                    expected_output=f"Detailed results of {task_config['description']}",
                    context=task_context,  # Enhanced structured context
                    async_execution=False,  # Sequential execution for better control
                    output_file=os.path.join(output_dir, f"{task_id}.json"),
                    priority=priority,  # Tasks with more dependencies get higher priority
                    verbose=self.verbose  # Use the verbose parameter from constructor
                )
            
            # Create crew with process type and other parameters from constructor
            logger.info(f"Creating crew with process type: {self.process_type}")
            self.crew = Crew(
                agents=list(self.agents.values()),
                tasks=[],  # Tasks will be added dynamically based on dependencies
                process=self.process_type,  # Use process type from constructor
                manager_llm=self.model,
                cache=True,  # Enable caching with the built-in cache
                memory=self.memory_enabled,  # Use memory parameter from constructor
                verbose=self.verbose,  # Use verbose parameter from constructor
                max_rpm=30,  # Rate limiting to prevent API throttling
                step_callback=self._step_callback  # Add callback for progress monitoring
            )
            
            logger.info(f"Crew initialized successfully with process={self.process_type}, memory={self.memory_enabled}, delegation={self.allow_delegation}")
        
        except Exception as e:
            logger.error(f"Error initializing crew: {str(e)}")
            raise
            
    def _step_callback(self, step_output):
        """Callback function for monitoring crew execution progress"""
        try:
            # Extract information from step output
            agent_name = step_output.agent.role if hasattr(step_output, 'agent') else "Unknown Agent"
            task_description = step_output.task.description if hasattr(step_output, 'task') else "Unknown Task"
            task_status = step_output.status if hasattr(step_output, 'status') else "in_progress"
            
            # Log progress information
            logger.info(f"Step progress - Agent: {agent_name}, Task: {task_description}, Status: {task_status}")
            
            # Create step log file
            step_log_file = os.path.join(self.results_dir, f"sprint_{self.sprint_counter}", "step_logs.json")
            
            # Initialize file if it doesn't exist
            if not os.path.exists(step_log_file):
                with open(step_log_file, 'w') as f:
                    json.dump({"steps": []}, f, indent=2)
            
            # Read existing logs
            with open(step_log_file, 'r') as f:
                logs = json.load(f)
            
            # Add new log
            logs["steps"].append({
                "agent": agent_name,
                "task": task_description,
                "status": task_status,
                "timestamp": datetime.now().isoformat()
            })
            
            # Write updated logs
            with open(step_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Error in step callback: {str(e)}")
            # Don't fail the entire process for a callback error
    
    def run(self) -> Dict[str, Any]:
        """
        Run the Dev Team crew with enhanced error recovery and checkpointing.
        
        Returns:
            Dict[str, Any]: The results of the crew run
        """
        try:
            # Skip execution in reset mode
            if self.reset_mode:
                return {"status": "skipped", "reason": "Reset mode active"}
            
            # Skip execution in chat mode
            if self.chat_mode:
                return {"status": "skipped", "reason": "Chat mode active"}
            
            # Create sprint directory
            sprint_dir = os.path.join(self.results_dir, f"sprint_{self.sprint_counter}")
            os.makedirs(sprint_dir, exist_ok=True)
            
            # Create checkpoints directory
            checkpoints_dir = os.path.join(sprint_dir, "checkpoints")
            os.makedirs(checkpoints_dir, exist_ok=True)
            
            # Execute tasks in dependency order
            task_outputs = {}
            execution_order = self._get_execution_order()
            
            # Check for existing checkpoint
            checkpoint_file = os.path.join(checkpoints_dir, "checkpoint.json")
            if os.path.exists(checkpoint_file):
                try:
                    with open(checkpoint_file, 'r') as f:
                        checkpoint_data = json.load(f)
                        task_outputs = checkpoint_data.get("task_outputs", {})
                        completed_tasks = checkpoint_data.get("completed_tasks", [])
                        
                        logger.info(f"Loaded checkpoint with {len(completed_tasks)} completed tasks")
                        
                        # Skip tasks that were already completed
                        execution_order = [t for t in execution_order if t not in completed_tasks]
                except Exception as e:
                    logger.warning(f"Error loading checkpoint: {str(e)}. Starting from beginning.")
                    task_outputs = {}
            
            completed_tasks = []
            
            for task_id in execution_order:
                logger.info(f"Executing task: {task_id}")
                
                # Get task configuration
                task_config = self.tasks_config[task_id]
                
                # Get task dependencies
                dependencies = task_config.get("dependencies", [])
                
                # Add dependency outputs to task context
                context = []
                for dep_id in dependencies:
                    if dep_id in task_outputs:
                        context.append(task_outputs[dep_id])
                
                # Set task context
                self.tasks[task_id].context = context
                
                # Add task to crew
                self.crew.tasks = [self.tasks[task_id]]
                
                # Execute task with retry logic
                max_retries = 3
                retry_count = 0
                last_error = None
                
                while retry_count < max_retries:
                    try:
                        # Execute task
                        result = self.crew.kickoff()
                        
                        # Store task output
                        task_outputs[task_id] = result
                        completed_tasks.append(task_id)
                        
                        # Save checkpoint after each task
                        self._save_checkpoint(checkpoints_dir, task_outputs, completed_tasks)
                        
                        # Save task result to file
                        result_file = os.path.join(sprint_dir, f"{task_id}.json")
                        with open(result_file, 'w') as f:
                            json.dump({
                                "task_id": task_id,
                                "description": task_config["description"],
                                "agent": task_config["agent"],
                                "result": result[0] if isinstance(result, list) else str(result),
                                "timestamp": datetime.now().isoformat()
                            }, f, indent=2)
                        
                        logger.info(f"Task {task_id} completed successfully")
                        break  # Success, exit retry loop
                        
                    except Exception as e:
                        retry_count += 1
                        last_error = e
                        backoff_time = 2 ** retry_count  # Exponential backoff
                        
                        logger.warning(f"Task {task_id} failed (attempt {retry_count}/{max_retries}): {str(e)}")
                        logger.info(f"Retrying in {backoff_time} seconds...")
                        
                        time.sleep(backoff_time)
                
                # If all retries failed, handle the error
                if retry_count == max_retries and last_error:
                    logger.error(f"Task {task_id} failed after {max_retries} attempts: {str(last_error)}")
                    
                    # Create error report
                    error_file = os.path.join(sprint_dir, f"{task_id}_error.json")
                    with open(error_file, 'w') as f:
                        json.dump({
                            "task_id": task_id,
                            "description": task_config["description"],
                            "error": str(last_error),
                            "timestamp": datetime.now().isoformat()
                        }, f, indent=2)
                    
                    # Consider whether to continue or abort based on task importance
                    if task_id in ["requirements_analysis", "architecture_design"]:
                        # Critical tasks - abort if they fail
                        raise Exception(f"Critical task {task_id} failed: {str(last_error)}")
                    else:
                        # Non-critical tasks - continue with next task
                        logger.warning(f"Continuing despite failure of task {task_id}")
            
            # Create sprint summary with detailed status
            sprint_summary = {
                "sprint": self.sprint_counter,
                "project_goal": self.project_goal,
                "codebase_dir": self.codebase_dir,
                "tasks": list(execution_order),
                "completed_tasks": completed_tasks,
                "completed": len(completed_tasks) == len(self.tasks_config),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save sprint summary
            summary_file = os.path.join(sprint_dir, "sprint_summary.json")
            with open(summary_file, 'w') as f:
                json.dump(sprint_summary, f, indent=2)
            
            # Clean up checkpoints if sprint completed successfully
            if sprint_summary["completed"]:
                try:
                    import shutil
                    shutil.rmtree(checkpoints_dir)
                except Exception as e:
                    logger.warning(f"Could not clean up checkpoints: {str(e)}")
            
            # Increment sprint counter
            self.sprint_counter += 1
            
            logger.info(f"Sprint {self.sprint_counter-1} completed successfully")
            
            return sprint_summary
        
        except Exception as e:
            logger.error(f"Error running crew: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "sprint": self.sprint_counter,
                "timestamp": datetime.now().isoformat()
            }
    
    def _save_checkpoint(self, checkpoints_dir: str, task_outputs: Dict[str, Any], completed_tasks: List[str]):
        """Save a checkpoint of the current progress."""
        try:
            checkpoint_data = {
                "timestamp": datetime.now().isoformat(),
                "completed_tasks": completed_tasks,
                "task_outputs": task_outputs
            }
            
            checkpoint_file = os.path.join(checkpoints_dir, "checkpoint.json")
            
            # Create a backup of the previous checkpoint
            if os.path.exists(checkpoint_file):
                backup_file = os.path.join(checkpoints_dir, f"checkpoint_{int(time.time())}.bak")
                try:
                    import shutil
                    shutil.copy2(checkpoint_file, backup_file)
                except Exception as e:
                    logger.warning(f"Failed to create checkpoint backup: {str(e)}")
            
            # Write the new checkpoint
            with open(checkpoint_file, 'w') as f:
                # Convert complex objects to strings for serialization
                serializable_outputs = {}
                for task_id, output in task_outputs.items():
                    serializable_outputs[task_id] = output[0] if isinstance(output, list) else str(output)
                
                checkpoint_data["task_outputs"] = serializable_outputs
                json.dump(checkpoint_data, f, indent=2)
                
            logger.info(f"Checkpoint saved with {len(completed_tasks)} completed tasks")
            
        except Exception as e:
            logger.warning(f"Failed to save checkpoint: {str(e)}")
    
    def _get_execution_order(self) -> List[str]:
        """
        Get the execution order of tasks based on dependencies.
        
        Returns:
            List[str]: List of task IDs in execution order
        """
        # Create dependency graph
        graph = {}
        for task_id, task_config in self.tasks_config.items():
            graph[task_id] = task_config.get("dependencies", [])
        
        # Topological sort
        visited = set()
        temp = set()
        order = []
        
        def visit(task_id):
            if task_id in temp:
                raise ValueError(f"Circular dependency found involving {task_id}")
            if task_id in visited:
                return
            
            temp.add(task_id)
            for dep_id in graph.get(task_id, []):
                visit(dep_id)
            
            temp.remove(task_id)
            visited.add(task_id)
            order.append(task_id)
        
        for task_id in graph:
            if task_id not in visited:
                visit(task_id)
        
        # Reverse to get correct execution order
        return list(reversed(order))
    
    def replay_task(self, task_index: int) -> Dict[str, Any]:
        """
        Replay a specific task.
        
        Args:
            task_index (int): Index of the task to replay
            
        Returns:
            Dict[str, Any]: The results of the task replay
        """
        try:
            # Initialize crew if not already initialized
            if self.crew is None:
                self._initialize_crew()
            
            # Get task IDs in execution order
            execution_order = self._get_execution_order()
            
            # Validate task index
            if task_index < 0 or task_index >= len(execution_order):
                raise ValueError(f"Task index {task_index} out of range (0-{len(execution_order)-1})")
            
            # Get task ID
            task_id = execution_order[task_index]
            
            # Get task configuration
            task_config = self.tasks_config[task_id]
            
            logger.info(f"Replaying task: {task_id}")
            
            # Execute task without dependencies
            self.tasks[task_id].context = []
            result = self.crew.execute_task(self.tasks[task_id])
            
            # Create replay directory
            replay_dir = os.path.join(self.results_dir, "replays")
            os.makedirs(replay_dir, exist_ok=True)
            
            # Save task result to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = os.path.join(replay_dir, f"{task_id}_{timestamp}.json")
            with open(result_file, 'w') as f:
                json.dump({
                    "task_id": task_id,
                    "description": task_config["description"],
                    "agent": task_config["agent"],
                    "result": result.raw,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
            
            logger.info(f"Task {task_id} replay completed")
            
            return {
                "task_id": task_id,
                "description": task_config["description"],
                "agent": task_config["agent"],
                "result": result.raw,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error replaying task: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def reset_memory(self, memory_type: str = "all") -> Dict[str, Any]:
        """
        Reset agent memory of the specified type.
        
        Args:
            memory_type (str, optional): Type of memory to reset. Defaults to "all".
            
        Returns:
            Dict[str, Any]: The results of the memory reset
        """
        try:
            # Initialize cache
            cache = AgentCache()
            
            # Reset cache based on memory type
            if memory_type == "all":
                cache.reset()
            else:
                cache.reset(memory_type)
            
            logger.info(f"Memory reset completed for type: {memory_type}")
            
            return {
                "status": "success",
                "memory_type": memory_type,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error resetting memory: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def process_chat(self, messages: List[Dict[str, str]], model: str = "default", workspace_context: Dict[str, Any] = None) -> str:
        """Process a chat message and return a response"""
        try:
            # Initialize chat mode if not already in it
            if not self.chat_mode:
                self.chat_mode = True
                self._initialize_crew()
            
            # Get the project manager agent
            project_manager = self.agents.get("project_manager")
            if not project_manager:
                raise ValueError("Project Manager agent not initialized")
            
            # Create a chat task
            chat_task = Task(
                description=f"Process chat message: {messages[-1]['content']}",
                agent=project_manager,
                context={
                    "messages": messages,
                    "workspace_context": workspace_context or {},
                    "current_dir": self.codebase_dir
                }
            )
            
            # Execute the chat task
            result = chat_task.execute()
            
            # Return the response
            return result.raw_output
            
        except Exception as e:
            logger.error(f"Error processing chat: {str(e)}")
            return f"I encountered an error: {str(e)}"