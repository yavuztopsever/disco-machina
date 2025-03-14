#!/usr/bin/env python3
"""
Main entry point for the Dev Team module.
This module provides the command-line interface for interacting with the Dev Team.
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

from .crew import DevTeamCrew
from .server import run_server

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("dev_team")

def setup_environment() -> Dict[str, str]:
    """
    Set up environment variables for the Dev Team.
    
    Returns:
        Dict[str, str]: Dictionary containing environment variables
    """
    # Load environment variables from .env file if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv not installed, skipping .env file loading")
    
    # Check for required environment variables
    required_env_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your environment or .env file")
        sys.exit(1)
    
    # Return environment configuration
    return {
        "openai_api_key": os.environ.get("OPENAI_API_KEY"),
        "brave_api_key": os.environ.get("BRAVE_API_KEY"),
        "github_token": os.environ.get("GH_TOKEN")
    }

def run_dev_team(project_goal: str, codebase_dir: str, interactive: bool = True) -> Dict[str, Any]:
    """
    Run the Dev Team with the specified project goal and codebase directory.
    
    Args:
        project_goal (str): The goal of the project
        codebase_dir (str): The directory containing the codebase
        interactive (bool, optional): Whether to run in interactive mode. Defaults to True.
        
    Returns:
        Dict[str, Any]: The results of the Dev Team run
    """
    # Set up environment
    env_config = setup_environment()
    
    # Create absolute path for codebase directory
    codebase_path = Path(codebase_dir).resolve()
    if not codebase_path.exists():
        logger.info(f"Creating directory {codebase_path}")
        codebase_path.mkdir(parents=True, exist_ok=True)
    
    # Create Dev Team crew
    logger.info(f"Creating Dev Team crew for project: {project_goal}")
    logger.info(f"Using codebase directory: {codebase_path}")
    
    crew = DevTeamCrew(
        project_goal=project_goal,
        codebase_dir=str(codebase_path),
        interactive=interactive
    )
    
    # Run the crew
    logger.info("Starting Dev Team crew...")
    result = crew.run()
    
    logger.info("Dev Team completed!")
    return result

def train_dev_team(num_iterations: int, output_file: str, project_goal: str, codebase_dir: str) -> Dict[str, Any]:
    """
    Train the Dev Team with the specified number of iterations.
    
    Args:
        num_iterations (int): Number of training iterations
        output_file (str): Path to the output file for training results
        project_goal (str): The goal for the training project
        codebase_dir (str): The directory containing the training codebase
        
    Returns:
        Dict[str, Any]: The results of the training
    """
    env_config = setup_environment()
    
    # Create absolute path for codebase directory
    codebase_path = Path(codebase_dir).resolve()
    if not codebase_path.exists():
        logger.info(f"Creating directory {codebase_path}")
        codebase_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Training Dev Team for {num_iterations} iterations")
    logger.info(f"Using project goal: {project_goal}")
    logger.info(f"Using codebase directory: {codebase_path}")
    
    crew = DevTeamCrew(
        project_goal=project_goal,
        codebase_dir=str(codebase_path),
        training_mode=True
    )
    
    results = []
    for i in range(num_iterations):
        logger.info(f"Starting training iteration {i+1}/{num_iterations}")
        result = crew.run()
        results.append(result)
    
    # Save results to output file
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Training completed! Results saved to {output_file}")
    return {"iterations": num_iterations, "results": results}

def test_dev_team(num_iterations: int, model: str, project_goal: str, codebase_dir: str) -> Dict[str, Any]:
    """
    Test the Dev Team with the specified number of iterations.
    
    Args:
        num_iterations (int): Number of test iterations
        model (str): Model to use for testing (e.g., "gpt-4")
        project_goal (str): The goal for the test project
        codebase_dir (str): The directory containing the test codebase
        
    Returns:
        Dict[str, Any]: The results of the testing
    """
    env_config = setup_environment()
    
    # Create absolute path for codebase directory
    codebase_path = Path(codebase_dir).resolve()
    if not codebase_path.exists():
        logger.info(f"Creating directory {codebase_path}")
        codebase_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Testing Dev Team for {num_iterations} iterations with model {model}")
    logger.info(f"Using project goal: {project_goal}")
    logger.info(f"Using codebase directory: {codebase_path}")
    
    crew = DevTeamCrew(
        project_goal=project_goal,
        codebase_dir=str(codebase_path),
        model=model,
        test_mode=True
    )
    
    results = []
    for i in range(num_iterations):
        logger.info(f"Starting test iteration {i+1}/{num_iterations}")
        result = crew.run()
        results.append(result)
    
    logger.info("Testing completed!")
    return {"iterations": num_iterations, "model": model, "results": results}

def replay_task(task_index: int) -> Dict[str, Any]:
    """
    Replay a specific task.
    
    Args:
        task_index (int): Index of the task to replay
        
    Returns:
        Dict[str, Any]: The results of the task replay
    """
    env_config = setup_environment()
    
    logger.info(f"Replaying task with index {task_index}")
    
    crew = DevTeamCrew(
        project_goal="Replay task",
        codebase_dir=".",
        replay_mode=True
    )
    
    result = crew.replay_task(task_index)
    
    logger.info("Task replay completed!")
    return result

def reset_memory(memory_type: str = "all") -> Dict[str, Any]:
    """
    Reset agent memory of the specified type.
    
    Args:
        memory_type (str, optional): Type of memory to reset. Defaults to "all".
        
    Returns:
        Dict[str, Any]: The results of the memory reset
    """
    from .crew import DevTeamCrew
    
    logger.info(f"Resetting {memory_type} memory")
    
    crew = DevTeamCrew(
        project_goal="Reset memory",
        codebase_dir=".",
        reset_mode=True
    )
    
    result = crew.reset_memory(memory_type)
    
    logger.info(f"{memory_type} memory reset completed!")
    return result

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Dev Team - AI-powered development team")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run the Dev Team")
    run_parser.add_argument("project_goal", nargs="?", help="Project goal")
    run_parser.add_argument("codebase_dir", nargs="?", default=".", help="Codebase directory")
    run_parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode")
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Train the Dev Team")
    train_parser.add_argument("iterations", type=int, help="Number of training iterations")
    train_parser.add_argument("output_file", help="Output file for training results")
    train_parser.add_argument("project_goal", help="Project goal for training")
    train_parser.add_argument("codebase_dir", help="Codebase directory for training")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test the Dev Team")
    test_parser.add_argument("iterations", type=int, help="Number of test iterations")
    test_parser.add_argument("model", help="Model to use for testing")
    test_parser.add_argument("project_goal", help="Project goal for testing")
    test_parser.add_argument("codebase_dir", help="Codebase directory for testing")
    
    # Replay command
    replay_parser = subparsers.add_parser("replay", help="Replay a task")
    replay_parser.add_argument("task_index", type=int, help="Index of the task to replay")
    
    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset agent memory")
    reset_parser.add_argument("--type", default="all", help="Type of memory to reset")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run the API server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Server host")
    server_parser.add_argument("--port", type=int, default=8000, help="Server port")
    server_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "run":
        if not args.project_goal:
            parser.error("Project goal is required")
        result = run_dev_team(args.project_goal, args.codebase_dir, not args.non_interactive)
        print(json.dumps(result, indent=2))
    
    elif args.command == "train":
        result = train_dev_team(args.iterations, args.output_file, args.project_goal, args.codebase_dir)
        print(json.dumps(result, indent=2))
    
    elif args.command == "test":
        result = test_dev_team(args.iterations, args.model, args.project_goal, args.codebase_dir)
        print(json.dumps(result, indent=2))
    
    elif args.command == "replay":
        result = replay_task(args.task_index)
        print(json.dumps(result, indent=2))
    
    elif args.command == "reset":
        result = reset_memory(args.type)
        print(json.dumps(result, indent=2))
    
    elif args.command == "server":
        run_server(host=args.host, port=args.port, reload=args.reload)
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())