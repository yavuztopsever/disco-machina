"""
Main entry point for the Dev Team - a crew of specialized AI agents that collaborate on software projects.
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from crewai import Agent, Crew, Process, Task
import yaml

from .crew import create_project_manager, create_software_architect, create_fullstack_developer, create_test_engineer
from .tools.dev_tools import (
    RequirementsAnalysisTool, TaskTrackingTool, AgileProjectManagementTool,
    CodeAnalysisTool, CodebaseAnalysisTool, CodeRefactoringTool, ObsoleteCodeCleanupTool,
    CodeImplementationTool, CodeGenerationTool, DependencyManagementTool,
    TestGenerationTool, TestRunnerTool, CodeCoverageTool, CodeReviewTool,
)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def create_output_directory(project_name: str) -> str:
    """Create an output directory for the project results."""
    base_dir = "results"
    os.makedirs(base_dir, exist_ok=True)
    
    # Create a timestamped folder
    timestamp = int(time.time())
    project_dir = f"{base_dir}/{project_name}_{timestamp}"
    os.makedirs(project_dir, exist_ok=True)
    
    return project_dir


def get_agent_tools(agent_role: str) -> List[Any]:
    """Get tools for a specific agent role."""
    tools_mapping = {
        "project_manager": [
            RequirementsAnalysisTool(),
            TaskTrackingTool(),
            AgileProjectManagementTool(),
        ],
        "software_architect": [
            CodeAnalysisTool(),
            CodebaseAnalysisTool(),
            CodeRefactoringTool(),
            ObsoleteCodeCleanupTool(),
        ],
        "fullstack_developer": [
            CodeImplementationTool(), 
            CodeGenerationTool(),
            DependencyManagementTool(),
        ],
        "test_engineer": [
            TestGenerationTool(),
            TestRunnerTool(),
            CodeCoverageTool(),
            CodeReviewTool(),
        ]
    }
    
    return tools_mapping.get(agent_role, [])


def create_tasks(agents: Dict[str, Agent], project_goal: str, codebase_dir: str) -> List[Task]:
    """Create tasks for the crew based on agents and project goal."""
    tasks_config = load_config(os.path.join(os.path.dirname(__file__), "config", "tasks.yaml"))
    
    tasks = []
    for task_config in tasks_config["tasks"]:
        agent = agents[task_config["agent"]]
        
        # Replace placeholders in task description
        description = task_config["description"].format(
            project_goal=project_goal,
            codebase_dir=codebase_dir
        )
        
        # Create task with dependencies if specified
        dependency_ids = task_config.get("depends_on", [])
        dependencies = [tasks[dep_id] for dep_id in dependency_ids] if dependency_ids else None
        
        task = Task(
            description=description,
            agent=agent,
            expected_output=task_config.get("expected_output", "Detailed report"),
            dependencies=dependencies,
            context=task_config.get("context", None)
        )
        tasks.append(task)
    
    return tasks


def create_agents(project_goal: str, codebase_dir: str, verbose: bool = False) -> Dict[str, Agent]:
    """Create all agents for the crew."""
    agents = {
        "project_manager": create_project_manager(
            tools=get_agent_tools("project_manager"),
            verbose=verbose
        ),
        "software_architect": create_software_architect(
            tools=get_agent_tools("software_architect"),
            verbose=verbose
        ),
        "fullstack_developer": create_fullstack_developer(
            tools=get_agent_tools("fullstack_developer"),
            verbose=verbose
        ),
        "test_engineer": create_test_engineer(
            tools=get_agent_tools("test_engineer"),
            verbose=verbose
        )
    }
    
    return agents


def setup_crew(project_goal: str, codebase_dir: str, verbose: bool = False) -> Tuple[Crew, List[Task]]:
    """Set up the crew with agents and tasks."""
    agents = create_agents(project_goal, codebase_dir, verbose)
    tasks = create_tasks(agents, project_goal, codebase_dir)
    
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        verbose=verbose,
        process=Process.hierarchical
    )
    
    return crew, tasks


def run_dev_team(project_goal: str, codebase_dir: str, verbose: bool = False) -> None:
    """Run the Dev Team crew on a project."""
    print(f"🚀 Starting Dev Team to work on: {project_goal}")
    
    # Create output directory
    project_name = project_goal.lower().replace(" ", "_")[:20]
    output_dir = create_output_directory(project_name)
    print(f"📁 Project outputs will be saved to: {output_dir}")
    
    # Set up crew and tasks
    crew, tasks = setup_crew(project_goal, codebase_dir, verbose)
    
    # Execute crew
    result = crew.kickoff()
    
    # Save results
    with open(f"{output_dir}/result.json", "w") as f:
        json.dump({
            "project_goal": project_goal,
            "codebase_dir": codebase_dir,
            "result": result
        }, f, indent=2)
    
    print(f"✅ Dev Team completed their work! Results saved to {output_dir}/result.json")
    

def train_dev_team(num_iterations: int, output_file: str, project_goal: str, codebase_dir: str) -> None:
    """Train the Dev Team by running multiple iterations and collecting results."""
    results = []
    
    for i in range(num_iterations):
        print(f"🔄 Starting training iteration {i+1}/{num_iterations}")
        
        start_time = time.time()
        crew, tasks = setup_crew(project_goal, codebase_dir)
        result = crew.kickoff()
        end_time = time.time()
        
        results.append({
            "iteration": i+1,
            "duration": end_time - start_time,
            "result": result
        })
        
        print(f"✅ Completed iteration {i+1}/{num_iterations}")
    
    # Save training results
    with open(output_file, "w") as f:
        json.dump({
            "project_goal": project_goal,
            "codebase_dir": codebase_dir,
            "num_iterations": num_iterations,
            "results": results
        }, f, indent=2)
    
    print(f"🎓 Training completed! Results saved to {output_file}")


def test_dev_team(num_iterations: int, model: str, project_goal: str, codebase_dir: str) -> None:
    """Test the Dev Team with a specific model."""
    results = []
    
    for i in range(num_iterations):
        print(f"🧪 Starting test iteration {i+1}/{num_iterations} with model: {model}")
        
        # Temporarily override the model
        os.environ["OPENAI_MODEL_NAME"] = model
        
        start_time = time.time()
        crew, tasks = setup_crew(project_goal, codebase_dir)
        result = crew.kickoff()
        end_time = time.time()
        
        results.append({
            "iteration": i+1,
            "model": model,
            "duration": end_time - start_time,
            "result": result
        })
        
        print(f"✅ Completed test iteration {i+1}/{num_iterations}")
    
    # Reset environment variable
    if "OPENAI_MODEL_NAME" in os.environ:
        del os.environ["OPENAI_MODEL_NAME"]
    
    # Save test results to a file with timestamp
    timestamp = int(time.time())
    output_file = f"test_results_{model}_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump({
            "project_goal": project_goal,
            "codebase_dir": codebase_dir,
            "model": model,
            "num_iterations": num_iterations,
            "results": results
        }, f, indent=2)
    
    print(f"🧪 Testing completed! Results saved to {output_file}")


def replay_task(task_id: int) -> None:
    """Replay a specific task from the task list."""
    # Load tasks config
    tasks_config = load_config(os.path.join(os.path.dirname(__file__), "config", "tasks.yaml"))
    
    if 0 <= task_id < len(tasks_config["tasks"]):
        task_config = tasks_config["tasks"][task_id]
        agent_role = task_config["agent"]
        
        print(f"🔄 Replaying task {task_id}: {task_config['description']}")
        print(f"👤 Agent: {agent_role}")
        
        # Create agent
        agents = {
            "project_manager": create_project_manager(
                tools=get_agent_tools("project_manager"),
                verbose=True
            ),
            "software_architect": create_software_architect(
                tools=get_agent_tools("software_architect"),
                verbose=True
            ),
            "fullstack_developer": create_fullstack_developer(
                tools=get_agent_tools("fullstack_developer"),
                verbose=True
            ),
            "test_engineer": create_test_engineer(
                tools=get_agent_tools("test_engineer"),
                verbose=True
            )
        }
        
        agent = agents[agent_role]
        
        # Create task
        task = Task(
            description=task_config["description"].format(
                project_goal="Replay task example",
                codebase_dir="."
            ),
            agent=agent,
            expected_output=task_config.get("expected_output", "Detailed report")
        )
        
        # Execute task
        result = task.execute()
        
        # Save result
        timestamp = int(time.time())
        output_file = f"task_{task_id}_replay_{timestamp}.txt"
        
        with open(output_file, "w") as f:
            f.write(result)
        
        print(f"✅ Task replay completed! Result saved to {output_file}")
    else:
        print(f"❌ Invalid task ID. Must be between 0 and {len(tasks_config['tasks'])-1}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Dev Team - AI Agent Crew for Software Development")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run the Dev Team on a project")
    run_parser.add_argument("project_goal", help="Project goal or description")
    run_parser.add_argument("codebase_dir", help="Directory containing the codebase")
    run_parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Train the Dev Team through multiple iterations")
    train_parser.add_argument("iterations", type=int, help="Number of training iterations")
    train_parser.add_argument("output_file", help="File to save training results")
    train_parser.add_argument("project_goal", help="Project goal or description")
    train_parser.add_argument("codebase_dir", help="Directory containing the codebase")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test the Dev Team with a specific model")
    test_parser.add_argument("iterations", type=int, help="Number of test iterations")
    test_parser.add_argument("model", help="Model to test with (e.g., gpt-4, gpt-3.5-turbo)")
    test_parser.add_argument("project_goal", help="Project goal or description")
    test_parser.add_argument("codebase_dir", help="Directory containing the codebase")
    
    # Replay command
    replay_parser = subparsers.add_parser("replay", help="Replay a specific task")
    replay_parser.add_argument("task_id", type=int, help="ID of the task to replay")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_dev_team(args.project_goal, args.codebase_dir, args.verbose)
    elif args.command == "train":
        train_dev_team(args.iterations, args.output_file, args.project_goal, args.codebase_dir)
    elif args.command == "test":
        test_dev_team(args.iterations, args.model, args.project_goal, args.codebase_dir)
    elif args.command == "replay":
        replay_task(args.task_id)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()