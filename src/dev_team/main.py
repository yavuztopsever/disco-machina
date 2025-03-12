#!/usr/bin/env python
import sys
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Try different import approaches to handle different execution contexts
try:
    from src.dev_team.crew import DevTeamCrew
except ImportError:
    try:
        from dev_team.crew import DevTeamCrew
    except ImportError:
        # If running directly from the dev_team directory
        from crew import DevTeamCrew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_environment() -> None:
    """Validate required environment variables are set"""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

def validate_codebase_dir(codebase_dir: str) -> None:
    """Validate the codebase directory exists"""
    if not os.path.exists(codebase_dir):
        # Create the directory if it doesn't exist
        os.makedirs(codebase_dir)
        logger.info(f"Created codebase directory: {codebase_dir}")

def run_crew(project_goal: str, codebase_dir: str, config_dir: Optional[str] = None, non_interactive: bool = False) -> Dict[str, Any]:
    """Run the development crew on a project
    
    Args:
        project_goal: The goal of the project
        codebase_dir: The directory where to store code
        config_dir: Optional directory containing configuration files
        non_interactive: If True, don't prompt for user input during execution
    """
    try:
        # Validate environment and inputs
        validate_environment()
        validate_codebase_dir(codebase_dir)
        
        # Create and run the crew
        crew = DevTeamCrew(config_dir)
        result = crew.run(project_goal, codebase_dir, non_interactive=non_interactive)
        
        # Save results
        results_dir = os.path.join(codebase_dir, "results")
        os.makedirs(results_dir, exist_ok=True)
        
        with open(os.path.join(results_dir, "execution_result.json"), "w") as f:
            json.dump(result, f, indent=2)
        
        # Log completion
        logger.info(f"Development crew completed successfully. Results saved to {results_dir}")
        return result
        
    except Exception as e:
        logger.error(f"Error running development crew: {str(e)}")
        raise

def train_crew(iterations: int, training_data: str, project_goal: str, codebase_dir: str) -> None:
    """Train the crew for a specific number of iterations using improved training pipeline"""
    try:
        # Validate inputs
        if iterations <= 0:
            raise ValueError("Number of iterations must be positive")
        
        # Process training data
        input_data = {}
        if os.path.exists(training_data):
            # If training_data is a file, load it
            if training_data.endswith('.json'):
                with open(training_data, 'r') as f:
                    input_data = json.load(f)
                logger.info(f"Loaded training data from {training_data}")
            elif training_data.endswith('.pkl'):
                # This might be a saved model file to continue training from
                input_data = {"saved_model": training_data}
                logger.info(f"Will continue training from model {training_data}")
            else:
                logger.warning(f"Unknown training data format: {training_data}")
        else:
            # If training_data is not a file, treat it as output filename
            input_data = {"output_file": training_data}
            logger.info(f"Will save training results to {training_data}")
        
        # Create crew
        crew = DevTeamCrew()
        
        # Load saved model if available
        if "saved_model" in input_data and os.path.exists(input_data["saved_model"]):
            crew.load_trained_model(input_data["saved_model"])
            
        # Set up output file
        output_file = input_data.get("output_file") or os.path.join(codebase_dir, "results", "trained_model.pkl")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Set up training inputs
        training_inputs = {
            "project_goal": project_goal,
            "codebase_dir": codebase_dir
        }
        
        # Add any additional inputs from the input data
        if "inputs" in input_data and isinstance(input_data["inputs"], dict):
            training_inputs.update(input_data["inputs"])
        
        # Run training with enhanced error recovery
        try:
            logger.info(f"Starting training for {iterations} iterations")
            results = crew.train(n_iterations=iterations, inputs=training_inputs, filename=output_file)
            
            # Save detailed results
            results_file = os.path.join(os.path.dirname(output_file), "training_details.json")
            with open(results_file, "w") as f:
                json.dump(results, f, indent=2)
                
            logger.info(f"Training completed successfully. Results saved to {output_file}")
            logger.info(f"Detailed training results saved to {results_file}")
            
        except KeyboardInterrupt:
            # Handle user interruption gracefully
            logger.warning("Training interrupted by user")
            
            # Try to save partial results
            try:
                interrupted_file = os.path.join(os.path.dirname(output_file), "interrupted_training.pkl")
                crew._save_trained_model(interrupted_file, {
                    "iterations_completed": "partial",
                    "interrupted": True,
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"Partial training results saved to {interrupted_file}")
            except Exception as e:
                logger.error(f"Failed to save partial results: {str(e)}")
                
            raise
            
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        
        # Enhanced error reporting
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise

def test_crew(iterations: int, model: str, project_goal: str, codebase_dir: str) -> None:
    """Test the crew with a specific model"""
    try:
        # Create crew with test configuration
        crew = DevTeamCrew()
        crew.default_llm = model
        
        # Run tests
        results = []
        for i in range(iterations):
            logger.info(f"Starting test iteration {i+1}/{iterations}")
            result = crew.run(project_goal, codebase_dir)
            results.append({
                "iteration": i + 1,
                "model": model,
                "result": result
            })
            
        # Save test results
        results_dir = os.path.join(codebase_dir, "results")
        os.makedirs(results_dir, exist_ok=True)
        
        with open(os.path.join(results_dir, f"test_results_{model}.json"), "w") as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Testing completed successfully. Results saved to {results_dir}")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        raise

def replay_task(task_index: int) -> None:
    """Replay a specific task from the last crew run"""
    try:
        # Create crew
        crew = DevTeamCrew()
        
        # Get tasks
        tasks = crew.get_tasks("Replay task", "replay")
        
        # Validate task index
        if task_index >= len(tasks):
            raise ValueError(f"Invalid task index: {task_index}. Max index is {len(tasks)-1}")
        
        # Replay the task
        task = tasks[task_index]
        result = task.execute()
        
        logger.info(f"Task replay completed with result: {result}")
        
    except Exception as e:
        logger.error(f"Error replaying task: {str(e)}")
        raise

def reset_memory(memory_type: str = 'all') -> None:
    """Reset memory of specified type"""
    try:
        # Create crew
        crew = DevTeamCrew()
        
        # Reset memory
        crew.reset_memories(memory_type)
        
        logger.info(f"Successfully reset {memory_type} memories")
        
    except Exception as e:
        logger.error(f"Error resetting memory: {str(e)}")
        raise

def main():
    """Run the development team crew with enhanced error handling and command options"""
    # Default project goal and codebase directory
    project_goal = "Improve code quality and implement best practices"
    codebase_dir = os.path.join(os.getcwd(), "test_project")
    non_interactive = False
    
    try:
        # Check for --non-interactive flag in any position
        if "--non-interactive" in sys.argv:
            non_interactive = True
            # Remove the flag from the arguments
            sys.argv.remove("--non-interactive")
            
        # Handle other global flags
        max_retries = 3  # Default value
        if "--max-retries" in sys.argv:
            idx = sys.argv.index("--max-retries")
            if idx + 1 < len(sys.argv):
                try:
                    max_retries = int(sys.argv[idx + 1])
                    # Remove flag and value
                    sys.argv.pop(idx)
                    sys.argv.pop(idx)
                except ValueError:
                    logger.warning(f"Invalid value for --max-retries: {sys.argv[idx + 1]}. Using default: {max_retries}")
        
        # Check for command line arguments
        if len(sys.argv) > 1:
            # Handle different command types
            if sys.argv[1] == "run":
                if len(sys.argv) > 2:
                    project_goal = sys.argv[2]
                if len(sys.argv) > 3:
                    codebase_dir = sys.argv[3]
                    
                # Validate and create codebase directory if needed
                validate_codebase_dir(codebase_dir)
                
                # Configure and run the crew
                dev_team = DevTeamCrew()
                
                # Add runtime config options
                runtime_config = {
                    "max_retries": max_retries,
                    "non_interactive": non_interactive
                }
                
                # Run with proper error handling
                try:
                    result = dev_team.run(project_goal, codebase_dir, non_interactive=non_interactive)
                    
                    # Log completion
                    logger.info("Development crew execution completed successfully")
                    return result
                    
                except Exception as e:
                    logger.error(f"Error during crew execution: {str(e)}")
                    import traceback
                    logger.error(f"Error details: {traceback.format_exc()}")
                    
                    # Return error result
                    return {
                        "error": str(e),
                        "status": "failed"
                    }
            
            elif sys.argv[1] == "train" and len(sys.argv) > 4:
                iterations = int(sys.argv[2])
                training_data = sys.argv[3]
                project_goal = sys.argv[4]
                codebase_dir = sys.argv[5] if len(sys.argv) > 5 else os.path.join(os.getcwd(), "test_project")
                
                train_crew(iterations, training_data, project_goal, codebase_dir)
                
            elif sys.argv[1] == "test" and len(sys.argv) > 4:
                iterations = int(sys.argv[2])
                model = sys.argv[3]
                project_goal = sys.argv[4]
                codebase_dir = sys.argv[5] if len(sys.argv) > 5 else os.path.join(os.getcwd(), "test_project")
                
                test_crew(iterations, model, project_goal, codebase_dir)
                
            elif sys.argv[1] == "replay" and len(sys.argv) > 2:
                task_index = int(sys.argv[2])
                replay_task(task_index)
                
            elif sys.argv[1] == "reset-memory":
                memory_type = sys.argv[2] if len(sys.argv) > 2 else 'all'
                reset_memory(memory_type)
                
            elif sys.argv[1] == "server":
                # Start the API server
                logger.info("Starting Dev Team API server")
                try:
                    # Import and run the server
                    from .server import start
                    start()
                except Exception as e:
                    logger.error(f"Error starting server: {str(e)}")
                    import traceback
                    logger.error(f"Error details: {traceback.format_exc()}")
                    return {
                        "error": str(e),
                        "status": "failed"
                    }
                
            elif sys.argv[1] == "test-unit":
                # Run unit tests for DevTeam itself
                import unittest
                
                # Define directory to look for tests
                test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "tests")
                
                # If specific test pattern provided, use it
                if len(sys.argv) > 2:
                    pattern = sys.argv[2]
                else:
                    pattern = "test_*.py"
                
                logger.info(f"Running unit tests from {test_dir} matching {pattern}")
                
                # Discover and run tests
                suite = unittest.defaultTestLoader.discover(test_dir, pattern=pattern)
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)
                
                # Return success/failure
                return {
                    "success": result.wasSuccessful(),
                    "tests_run": result.testsRun,
                    "failures": len(result.failures),
                    "errors": len(result.errors)
                }
                
            else:
                # Legacy mode: first arg is project goal
                project_goal = sys.argv[1]
                if len(sys.argv) > 2:
                    codebase_dir = sys.argv[2]
                    
                # Validate and create codebase directory if needed
                validate_codebase_dir(codebase_dir)
                
                # Run the crew
                dev_team = DevTeamCrew()
                
                # Run with proper error handling
                try:
                    result = dev_team.run(project_goal, codebase_dir, non_interactive=non_interactive)
                    
                    # Log completion
                    logger.info("Development crew execution completed successfully")
                    return result
                    
                except Exception as e:
                    logger.error(f"Error during crew execution: {str(e)}")
                    import traceback
                    logger.error(f"Error details: {traceback.format_exc()}")
                    
                    # Return error result
                    return {
                        "error": str(e),
                        "status": "failed"
                    }
        else:
            # No arguments, run with defaults
            # Validate and create codebase directory if needed
            validate_codebase_dir(codebase_dir)
            
            # Run the crew
            dev_team = DevTeamCrew()
            
            # Run with proper error handling
            try:
                result = dev_team.run(project_goal, codebase_dir, non_interactive=non_interactive)
                
                # Log completion
                logger.info("Development crew execution completed successfully")
                return result
                
            except Exception as e:
                logger.error(f"Error during crew execution: {str(e)}")
                import traceback
                logger.error(f"Error details: {traceback.format_exc()}")
                
                # Return error result
                return {
                    "error": str(e),
                    "status": "failed"
                }
    except Exception as e:
        logger.error(f"Unhandled error in main: {str(e)}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        
        # Return error result
        return {
            "error": str(e),
            "status": "failed"
        }

if __name__ == "__main__":
    main()
