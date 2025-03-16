# CrewAI Implementation Details

## Overview

This document outlines how the DiscoMachina system leverages CrewAI features to create a robust, efficient, and intelligent development team. The implementation focuses on creating a hierarchical team structure with specialized roles, task dependencies, and advanced features for context management, error recovery, and tool integration.

## 1. Agent Configuration

We've implemented a team of specialized agents with enhanced capabilities:

### Project Manager Agent

```yaml
role: "Project Manager"
goal: "Analyze requirements, create sprint plans, coordinate team, and ensure project success"
tools:
  # Domain-specific tools
  - "RequirementsAnalysisTool"
  - "TaskTrackingTool"
  - "AgileProjectManagementTool"
  # CrewAI built-in tools
  - "BraveSearchTool"
  - "DirectoryReadTool"
  - "FileReadTool"
  - "FileWriterTool"
  - "GithubSearchTool"
```

### Software Architect Agent

```yaml
role: "Software Architect"
goal: "Design system architecture, analyze code structure, recommend improvements, and ensure maintainable code"
tools:
  # Domain-specific tools
  - "CodeAnalysisTool"
  - "CodebaseAnalysisTool"
  - "CodeRefactoringTool"
  - "ObsoleteCodeCleanupTool"
  # CrewAI built-in tools
  - "CodeDocsSearchTool"
  - "DirectoryReadTool"
  - "FileReadTool"
  - "FileWriterTool"
  - "GithubSearchTool"
```

### Fullstack Developer Agent

```yaml
role: "Fullstack Developer"
goal: "Implement features, fix bugs, manage dependencies, and ensure code quality"
tools:
  # Domain-specific tools
  - "CodeImplementationTool"
  - "CodeGenerationTool"
  - "DependencyManagementTool"
  # CrewAI built-in tools
  - "CodeInterpreterTool"
  - "CodeDocsSearchTool"
  - "DirectoryReadTool"
  - "FileReadTool"
  - "FileWriterTool"
  - "GithubSearchTool"
  - "BraveSearchTool"
```

### Test Engineer Agent

```yaml
role: "Test Engineer"
goal: "Create tests, ensure code coverage, perform code reviews, and maintain code quality"
tools:
  # Domain-specific tools
  - "TestGenerationTool"
  - "TestRunnerTool"
  - "CodeCoverageTool"
  - "CodeReviewTool"
  # CrewAI built-in tools
  - "CodeInterpreterTool"
  - "DirectoryReadTool"
  - "FileReadTool"
  - "FileWriterTool"
  - "CodeDocsSearchTool"
  - "GithubSearchTool"
```

## 2. Advanced Agent Configuration

Each agent is configured with advanced CrewAI features:

```python
agent = Agent(
    role=agent_config["role"],
    goal=agent_config["goal"],
    backstory=agent_config["backstory"],
    verbose=agent_config.get("verbose", True),
    tools=agent_tools,
    allow_delegation=True,  # Enable hierarchical delegation
    memory=True,  # Enable memory for better context retention
    llm=self.model,
    max_rpm=30,  # Rate limiting to prevent API throttling
    max_iterations=10,  # Prevent infinite loops
    max_execution_time=1800,  # 30 minute timeout per agent action
)
```

## 3. Task Configuration

Tasks are configured with enhanced context and priority:

```python
task = Task(
    description=task_description,
    agent=self.agents[agent_id],
    expected_output=f"Detailed results of {task_config['description']}",
    context=task_context,  # Enhanced structured context
    async_execution=False,  # Sequential execution for better control
    output_file=os.path.join(results_dir, f"sprint_{sprint_counter}", f"{task_id}.json"),
    priority=priority  # Tasks with more dependencies get higher priority
)
```

## 4. Crew Configuration

The crew is set up with hierarchical process and advanced features:

```python
crew = Crew(
    agents=list(self.agents.values()),
    tasks=[],  # Tasks will be added dynamically based on dependencies
    process=Process.hierarchical,  # Leverage hierarchical capabilities
    manager_llm=self.model,
    cache=True,  # Enable caching with the built-in cache
    memory=True,  # Enable memory for better context retention
    verbose=True,  # Detailed logging
    max_rpm=30,  # Rate limiting to prevent API throttling
    step_callback=self._step_callback  # Add callback for progress monitoring
)
```

## 5. Tool Integration

The system integrates two types of tools:

### Domain-Specific Tools

These are custom tools designed for specific development tasks:

- RequirementsAnalysisTool
- TaskTrackingTool
- AgileProjectManagementTool
- CodeAnalysisTool
- CodebaseAnalysisTool
- CodeRefactoringTool
- ObsoleteCodeCleanupTool
- CodeImplementationTool
- CodeGenerationTool
- DependencyManagementTool
- TestGenerationTool
- TestRunnerTool
- CodeCoverageTool
- CodeReviewTool

### CrewAI Built-In Tools

These are standard tools provided by the CrewAI framework:

- BraveSearchTool: Enables web search capabilities through the Brave Search API
- CodeDocsSearchTool: Provides semantic search within code documentation
- CodeInterpreterTool: Executes Python code in a secure container
- DirectoryReadTool: Lists directory contents with enhanced features
- FileReadTool: Reads file contents with improved error handling
- FileWriterTool: Writes content to files with cross-platform compatibility
- GithubSearchTool: Provides semantic search for GitHub repositories

## 6. Error Recovery System

We've implemented a robust error recovery system with exponential backoff:

```python
# Execute task with retry logic
max_retries = 3
retry_count = 0
last_error = None

while retry_count < max_retries:
    try:
        # Execute task
        result = self.crew.kickoff()
        
        # Success - save results and exit retry loop
        task_outputs[task_id] = result
        completed_tasks.append(task_id)
        self._save_checkpoint(checkpoints_dir, task_outputs, completed_tasks)
        break
        
    except Exception as e:
        retry_count += 1
        last_error = e
        backoff_time = 2 ** retry_count  # Exponential backoff
        
        logger.warning(f"Task {task_id} failed (attempt {retry_count}/{max_retries}): {str(e)}")
        logger.info(f"Retrying in {backoff_time} seconds...")
        
        time.sleep(backoff_time)

# If all retries failed, handle based on task criticality
if retry_count == max_retries and last_error:
    if task_id in ["requirements_analysis", "architecture_design"]:
        # Critical tasks cause job failure
        raise Exception(f"Critical task {task_id} failed: {str(last_error)}")
    else:
        # Non-critical tasks allow continuing
        logger.warning(f"Continuing despite failure of task {task_id}")
```

## 7. Checkpointing System

We've implemented a checkpointing system for resilience:

```python
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
```

## 8. Progress Monitoring

We've implemented a callback system for real-time progress monitoring:

```python
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
```

## 9. Real-time Updates

We've implemented WebSocket support for real-time updates:

```python
# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
    
    async def send_update(self, job_id: str, data: Dict[str, Any]):
        if job_id in self.active_connections:
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.error(f"Error sending websocket update: {str(e)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        for job_id in self.active_connections:
            await self.send_update(job_id, message)
```

## 10. Context Management

We've implemented an advanced context management system:

```python
def compact_context():
    """Compact the context by summarizing older messages"""
    if supports_color():
        print(f"\n\033[38;5;93m====== COMPACTING CONTEXT ======\033[0m")
        print(f"\033[38;5;93mContext window approaching limit. Summarizing older messages...\033[0m")
    else:
        print("\n====== COMPACTING CONTEXT ======")
        print("Context window approaching limit. Summarizing older messages...")
    
    # Keep the 20% most recent messages
    keep_count = max(len(context_storage["messages"]) // 5, 10)  # At least keep 10 messages
    
    # Summarize older messages
    older_messages = context_storage["messages"][:-keep_count]
    recent_messages = context_storage["messages"][-keep_count:]
    
    # Create a summary of older messages
    summary = f"[SUMMARY: {len(older_messages)} previous messages compacted]"
    
    # Reset context with summary and recent messages
    context_storage["messages"] = [{"timestamp": "SUMMARY", "content": summary, "type": "system"}] + recent_messages
    
    # Recalculate token count (rough estimate)
    context_storage["token_count"] = sum(len(m["content"]) // 4 for m in context_storage["messages"])
```

## Key Benefits

The implementation provides several key benefits:

1. **Hierarchical Structure**: Efficient task delegation with clear role separation
2. **Resilience**: Checkpointing and error recovery for robust operation
3. **Real-time Updates**: WebSocket integration for instant progress updates
4. **Tool Integration**: Combining custom and built-in tools for maximum capability
5. **Context Management**: Advanced context handling for better conversations
6. **Performance Optimization**: Rate limiting and caching for efficient execution
7. **Progress Monitoring**: Step callbacks for detailed progress tracking