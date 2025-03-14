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
from .tools.dev_tools import (
    RequirementsAnalysisTool,
    TaskTrackingTool,
    AgileProjectManagementTool,
    CodeAnalysisTool,
    CodebaseAnalysisTool,
    CodeRefactoringTool,
    ObsoleteCodeCleanupTool,
    CodeImplementationTool,
    CodeGenerationTool,
    DependencyManagementTool,
    TestGenerationTool,
    TestRunnerTool,
    CodeCoverageTool,
    CodeReviewTool
)

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
        model: str = "gpt-4"
    ):
        """
        Initialize the Dev Team Crew.
        
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
        """Initialize the crew with agents and tasks"""
        try:
            # Initialize tools
            tools = {
                "RequirementsAnalysisTool": RequirementsAnalysisTool(),
                "TaskTrackingTool": TaskTrackingTool(),
                "AgileProjectManagementTool": AgileProjectManagementTool(),
                "CodeAnalysisTool": CodeAnalysisTool(),
                "CodebaseAnalysisTool": CodebaseAnalysisTool(),
                "CodeRefactoringTool": CodeRefactoringTool(),
                "ObsoleteCodeCleanupTool": ObsoleteCodeCleanupTool(),
                "CodeImplementationTool": CodeImplementationTool(),
                "CodeGenerationTool": CodeGenerationTool(),
                "DependencyManagementTool": DependencyManagementTool(),
                "TestGenerationTool": TestGenerationTool(),
                "TestRunnerTool": TestRunnerTool(),
                "CodeCoverageTool": CodeCoverageTool(),
                "CodeReviewTool": CodeReviewTool()
            }
            
            # Initialize agents
            self.agents = {}
            for agent_id, agent_config in self.agents_config.items():
                # Get agent tools
                agent_tools = []
                for tool_name in agent_config.get("tools", []):
                    if tool_name in tools:
                        agent_tools.append(tools[tool_name])
                
                # Create agent
                self.agents[agent_id] = Agent(
                    role=agent_config["role"],
                    goal=agent_config["goal"],
                    backstory=agent_config["backstory"],
                    verbose=agent_config.get("verbose", True),
                    tools=agent_tools,
                    allow_delegation=True,
                    llm=self.model
                )
            
            # Initialize tasks
            self.tasks = {}
            for task_id, task_config in self.tasks_config.items():
                # Check if agent exists
                agent_id = task_config["agent"]
                if agent_id not in self.agents:
                    logger.warning(f"Agent '{agent_id}' not found for task '{task_id}'")
                    continue
                
                # Create task description with context
                task_description = f"""
                Project Goal: {self.project_goal}
                Codebase Directory: {self.codebase_dir}
                Task: {task_config["description"]}
                
                Work on the codebase in {self.codebase_dir}.
                """
                
                # Create task
                self.tasks[task_id] = Task(
                    description=task_description,
                    agent=self.agents[agent_id],
                    expected_output=f"Detailed results of {task_config['description']}",
                    context=[]  # Context will be populated during execution
                )
            
            # Create crew with hierarchical process
            self.crew = Crew(
                agents=list(self.agents.values()),
                tasks=[],  # Tasks will be added dynamically based on dependencies
                process=Process.hierarchical,
                manager_llm=self.model,
                cache=AgentCache()
            )
            
            logger.info("Crew initialized successfully with agents and tasks")
        
        except Exception as e:
            logger.error(f"Error initializing crew: {str(e)}")
            raise
    
    def run(self) -> Dict[str, Any]:
        """
        Run the Dev Team crew.
        
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
            
            # Execute tasks in dependency order
            task_outputs = {}
            execution_order = self._get_execution_order()
            
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
                
                # Execute task
                result = self.crew.execute_task(self.tasks[task_id])
                
                # Store task output
                task_outputs[task_id] = result
                
                # Save task result to file
                result_file = os.path.join(sprint_dir, f"{task_id}.json")
                with open(result_file, 'w') as f:
                    json.dump({
                        "task_id": task_id,
                        "description": task_config["description"],
                        "agent": task_config["agent"],
                        "result": result.raw,
                        "timestamp": datetime.now().isoformat()
                    }, f, indent=2)
                
                logger.info(f"Task {task_id} completed")
            
            # Create sprint summary
            sprint_summary = {
                "sprint": self.sprint_counter,
                "project_goal": self.project_goal,
                "codebase_dir": self.codebase_dir,
                "tasks": list(execution_order),
                "completed": True,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save sprint summary
            summary_file = os.path.join(sprint_dir, "sprint_summary.json")
            with open(summary_file, 'w') as f:
                json.dump(sprint_summary, f, indent=2)
            
            # Increment sprint counter
            self.sprint_counter += 1
            
            logger.info(f"Sprint {self.sprint_counter-1} completed successfully")
            
            return sprint_summary
        
        except Exception as e:
            logger.error(f"Error running crew: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
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
        """
        Process a chat message and generate a response.
        
        Args:
            messages (List[Dict[str, str]]): List of chat messages
            model (str, optional): Model to use. Defaults to "default".
            workspace_context (Dict[str, Any], optional): Context about the workspace. Defaults to None.
            
        Returns:
            str: Response to the chat message
        """
        try:
            # Use openai directly for chat to avoid complexity of crew for simple chat
            import openai
            
            # Use environment variable for OpenAI API key
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            
            # Use specified model or default to GPT-4
            if model == "default":
                model = "gpt-4"
            
            # Add workspace context to system message
            if workspace_context:
                system_content = messages[0]["content"] if messages[0]["role"] == "system" else ""
                workspace_info = f"""
                Working directory: {workspace_context.get('path', 'N/A')}
                Project name: {workspace_context.get('name', 'N/A')}
                Config files: {', '.join(workspace_context.get('config_files', []))}
                Directories: {', '.join(workspace_context.get('directories', [][:5]))}
                """
                
                if messages[0]["role"] == "system":
                    messages[0]["content"] += f"\n\nWorkspace Context:\n{workspace_info}"
                else:
                    messages.insert(0, {
                        "role": "system",
                        "content": f"You are the Project Manager agent for a dev team. {workspace_info}"
                    })
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.7
            )
            
            # Return response text
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error processing chat: {str(e)}")
            return f"I'm sorry, I encountered an error: {str(e)}"