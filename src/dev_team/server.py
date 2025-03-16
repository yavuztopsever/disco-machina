#!/usr/bin/env python3
"""
API server for the Dev Team module.
This module provides a FastAPI-based server for interacting with the Dev Team.
"""

import os
import json
import logging
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .crew import DevTeamCrew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("dev_team_server")

# Create FastAPI app
app = FastAPI(
    title="Dev Team API Server",
    description="API server for interacting with the Dev Team for software development",
    version="0.1.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for job history
job_storage = {}

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

# Initialize connection manager
manager = ConnectionManager()

class ProjectRequest(BaseModel):
    """Project creation request model with enhanced CrewAI options"""
    project_goal: str = Field(..., description="Goal of the project")
    codebase_dir: str = Field(..., description="Directory containing the codebase")
    non_interactive: bool = Field(False, description="Whether to run in non-interactive mode")
    process_type: str = Field("hierarchical", description="CrewAI process type (sequential, parallel, or hierarchical)")
    model: Optional[str] = Field(None, description="LLM model to use")
    memory: bool = Field(True, description="Whether to enable agent memory")
    tools: str = Field("all", description="Comma-separated list of tools to enable, or 'all' for all tools")
    delegation: bool = Field(True, description="Whether to enable agent delegation")

class ChatRequest(BaseModel):
    """Chat request model"""
    messages: List[Dict[str, str]] = Field(..., description="Chat messages")
    model: str = Field("default", description="Model to use for the chat")
    workspace_context: Dict[str, Any] = Field({}, description="Context about the workspace")
    current_dir: str = Field(..., description="Current working directory of the client")
    memory: bool = Field(True, description="Whether to enable agent memory")

class TaskReplayRequest(BaseModel):
    """Task replay request model with enhanced CrewAI options"""
    task_index: int = Field(..., description="Index of the task to replay")
    process_type: str = Field("hierarchical", description="CrewAI process type (sequential, parallel, or hierarchical)")
    model: Optional[str] = Field(None, description="LLM model to use")
    memory: bool = Field(True, description="Whether to enable agent memory")
    tools: str = Field("all", description="Comma-separated list of tools to enable, or 'all' for all tools")
    verbose: bool = Field(True, description="Whether to enable verbose output")
    with_delegation: bool = Field(True, description="Whether to enable agent delegation")

class TrainRequest(BaseModel):
    """Training request model with enhanced CrewAI options"""
    project_goal: str = Field(..., description="Goal for the training session")
    codebase_dir: str = Field(..., description="Directory containing the codebase")
    iterations: int = Field(..., description="Number of training iterations")
    output_file: str = Field(..., description="File to save training results to")
    process_type: str = Field("hierarchical", description="CrewAI process type (sequential, parallel, or hierarchical)")
    model: Optional[str] = Field(None, description="LLM model to use")
    memory: bool = Field(True, description="Whether to enable agent memory")
    tools: str = Field("all", description="Comma-separated list of tools to enable, or 'all' for all tools")

class TestRequest(BaseModel):
    """Test request model with enhanced CrewAI options"""
    project_goal: str = Field(..., description="Goal for the test session")
    codebase_dir: str = Field(..., description="Directory containing the codebase")
    iterations: int = Field(..., description="Number of test iterations")
    model: str = Field(..., description="LLM model to test with")
    process_type: str = Field("hierarchical", description="CrewAI process type (sequential, parallel, or hierarchical)")
    memory: bool = Field(True, description="Whether to enable agent memory")
    tools: str = Field("all", description="Comma-separated list of tools to enable, or 'all' for all tools")

class MemoryResetRequest(BaseModel):
    """Memory reset request model"""
    memory_type: str = Field("all", description="Type of memory to reset")

async def process_job(job_id: str, project_request: ProjectRequest):
    """Process a job in the background with real-time updates"""
    try:
        # Update job status
        job_storage[job_id]["status"] = "initializing"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 0
        
        # Send status update via WebSocket
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "initializing",
            "message": "Initializing Dev Team crew...",
            "progress": 0,
            "timestamp": datetime.now().isoformat()
        })
        
        # Run the Dev Team
        from .crew import DevTeamCrew
        
        # Create absolute path for codebase directory
        codebase_path = Path(project_request.codebase_dir).resolve()
        if not codebase_path.exists():
            logger.info(f"Creating directory {codebase_path}")
            codebase_path.mkdir(parents=True, exist_ok=True)
            
            # Send update
            await manager.send_update(job_id, {
                "job_id": job_id,
                "status": "initializing",
                "message": f"Created directory: {codebase_path}",
                "progress": 10,
                "timestamp": datetime.now().isoformat()
            })
        
        # Update status
        job_storage[job_id]["status"] = "setting_up"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 20
        
        # Send status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "setting_up",
            "message": "Setting up Dev Team crew...",
            "progress": 20,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create Dev Team crew with enhanced CrewAI options
        logger.info(f"Creating Dev Team crew for project: {project_request.project_goal}")
        logger.info(f"Using codebase directory: {codebase_path}")
        logger.info(f"Process type: {project_request.process_type}")
        logger.info(f"Memory enabled: {project_request.memory}")
        logger.info(f"Tools: {project_request.tools}")
        
        # Determine model to use
        model = project_request.model if project_request.model else "gpt-4"
        logger.info(f"Using model: {model}")
        
        # Parse process type
        from crewai import Process
        process_map = {
            "sequential": Process.sequential,
            "parallel": Process.parallel,
            "hierarchical": Process.hierarchical
        }
        process_type = process_map.get(project_request.process_type, Process.hierarchical)
        
        # Parse tools list
        tools_list = None
        if project_request.tools != "all":
            tools_list = [tool.strip() for tool in project_request.tools.split(",")]
            logger.info(f"Using specific tools: {tools_list}")
        
        crew = DevTeamCrew(
            project_goal=project_request.project_goal,
            codebase_dir=str(codebase_path),
            interactive=not project_request.non_interactive,
            model=model,
            process_type=process_type,
            memory_enabled=project_request.memory,
            tools_list=tools_list,
            allow_delegation=project_request.delegation
        )
        
        # Update status
        job_storage[job_id]["status"] = "running"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 30
        
        # Send status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "running",
            "message": "Starting Dev Team crew execution...",
            "progress": 30,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create a progress monitoring task
        progress_task = asyncio.create_task(monitor_progress(job_id))
        
        # Run the crew
        logger.info("Starting Dev Team crew...")
        result = crew.run()
        
        # Cancel progress monitoring
        progress_task.cancel()
        
        # Update job status
        job_storage[job_id]["status"] = "completed"
        job_storage[job_id]["result"] = result
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 100
        
        # Send final status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "completed",
            "message": "Dev Team crew execution completed",
            "progress": 100,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Job {job_id} completed successfully")
    
    except Exception as e:
        # Update job status with error
        logger.error(f"Error processing job {job_id}: {str(e)}")
        job_storage[job_id]["status"] = "failed"
        job_storage[job_id]["result"] = {"error": str(e)}
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Send error update via WebSocket
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "failed",
            "message": f"Error: {str(e)}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

async def monitor_progress(job_id: str):
    """Monitor job progress and send periodic updates"""
    try:
        progress = 30
        while progress < 95:
            await asyncio.sleep(5)  # Update every 5 seconds
            
            # Skip if job is no longer running
            if job_id not in job_storage or job_storage[job_id]["status"] not in ["running", "setting_up"]:
                break
                
            # Increment progress (slower as we approach completion)
            increment = max(1, int((95 - progress) / 10))
            progress = min(95, progress + increment)
            
            # Update job storage
            job_storage[job_id]["progress"] = progress
            job_storage[job_id]["updated_at"] = datetime.now().isoformat()
            
            # Send progress update
            await manager.send_update(job_id, {
                "job_id": job_id,
                "status": job_storage[job_id]["status"],
                "message": f"Execution in progress ({progress}%)...",
                "progress": progress,
                "timestamp": datetime.now().isoformat()
            })
            
    except asyncio.CancelledError:
        logger.info(f"Progress monitoring for job {job_id} cancelled")
    except Exception as e:
        logger.error(f"Error monitoring progress for job {job_id}: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "timestamp": datetime.now().isoformat(),
        "active_websockets": {job_id: len(connections) for job_id, connections in manager.active_connections.items()}
    }
    
@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job updates"""
    try:
        await manager.connect(websocket, job_id)
        
        # Send initial status if job exists
        if job_id in job_storage:
            initial_data = {
                "job_id": job_id,
                "status": job_storage[job_id].get("status", "unknown"),
                "progress": job_storage[job_id].get("progress", 0),
                "message": "Connected to job monitor",
                "timestamp": datetime.now().isoformat()
            }
            if "result" in job_storage[job_id]:
                initial_data["result"] = job_storage[job_id]["result"]
                
            await websocket.send_json(initial_data)
        else:
            await websocket.send_json({
                "job_id": job_id,
                "status": "not_found",
                "message": "Job not found",
                "timestamp": datetime.now().isoformat()
            })
        
        # Keep connection open and handle messages
        while True:
            try:
                data = await websocket.receive_text()
                # Handle client messages if needed
            except WebSocketDisconnect:
                break
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
        logger.info(f"WebSocket client disconnected from job {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {str(e)}")
        try:
            await websocket.close()
        except:
            pass
        manager.disconnect(websocket, job_id)

@app.post("/projects", status_code=201)
async def create_project(project_request: ProjectRequest, background_tasks: BackgroundTasks):
    """Create a new project"""
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Store job information
    job_storage[job_id] = {
        "job_id": job_id,
        "project_goal": project_request.project_goal,
        "codebase_dir": project_request.codebase_dir,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "result": None
    }
    
    # Process the job in the background
    background_tasks.add_task(process_job, job_id, project_request)
    
    # Return job information
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Project creation queued successfully"
    }

@app.get("/projects")
async def list_projects():
    """List all projects"""
    return list(job_storage.values())

@app.get("/projects/{job_id}")
async def get_project(job_id: str):
    """Get project status"""
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return job_storage[job_id]

@app.post("/tasks/replay", status_code=202)
async def replay_task(task_request: TaskReplayRequest, background_tasks: BackgroundTasks):
    """Replay a task with enhanced CrewAI options"""
    try:
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        # Store job information with enhanced details
        job_storage[job_id] = {
            "job_id": job_id,
            "task_index": task_request.task_index,
            "process_type": task_request.process_type,
            "model": task_request.model,
            "memory_enabled": task_request.memory,
            "with_delegation": task_request.with_delegation,
            "verbose": task_request.verbose,
            "tools": task_request.tools,
            "status": "queued",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None
        }
        
        # Process the task replay in the background with enhanced options
        background_tasks.add_task(replay_task_job, job_id, task_request)
        
        # Return job information
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Task replay queued successfully",
            "task_index": task_request.task_index,
            "process_type": task_request.process_type,
            "memory_enabled": task_request.memory
        }
    except Exception as e:
        logger.error(f"Error queuing task replay: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def replay_task_job(job_id: str, task_request: TaskReplayRequest):
    """Process a task replay job in the background with enhanced CrewAI options"""
    try:
        # Update job status with initialization
        job_storage[job_id]["status"] = "initializing"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 0
        
        # Send status update via WebSocket
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "initializing",
            "message": "Initializing task replay...",
            "progress": 0,
            "timestamp": datetime.now().isoformat()
        })
        
        # Log task replay configuration
        logger.info(f"Replaying task {task_request.task_index}")
        logger.info(f"Process type: {task_request.process_type}")
        logger.info(f"Memory enabled: {task_request.memory}")
        logger.info(f"Agent delegation: {task_request.with_delegation}")
        logger.info(f"Verbose output: {task_request.verbose}")
        logger.info(f"Tools: {task_request.tools}")
        
        # Determine model to use
        model = task_request.model if task_request.model else "gpt-4"
        logger.info(f"Using model: {model}")
        
        # Parse process type
        from crewai import Process
        process_map = {
            "sequential": Process.sequential,
            "parallel": Process.parallel,
            "hierarchical": Process.hierarchical
        }
        process_type = process_map.get(task_request.process_type, Process.hierarchical)
        
        # Parse tools list
        tools_list = None
        if task_request.tools != "all":
            tools_list = [tool.strip() for tool in task_request.tools.split(",")]
            logger.info(f"Using specific tools: {tools_list}")
        
        # Update job status to setting up
        job_storage[job_id]["status"] = "setting_up"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 20
        
        # Send status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "setting_up",
            "message": "Setting up crew for task replay...",
            "progress": 20,
            "timestamp": datetime.now().isoformat()
        })
        
        # Run task replay with enhanced options
        from .crew import DevTeamCrew
        
        crew = DevTeamCrew(
            project_goal="Replay task",
            codebase_dir=".",
            replay_mode=True,
            model=model,
            process_type=process_type,
            memory_enabled=task_request.memory,
            tools_list=tools_list,
            verbose=task_request.verbose,
            allow_delegation=task_request.with_delegation
        )
        
        # Update job status to running
        job_storage[job_id]["status"] = "running"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 40
        
        # Send status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "running",
            "message": "Executing task replay...",
            "progress": 40,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create a progress monitoring task
        progress_task = asyncio.create_task(monitor_progress(job_id))
        
        # Execute the task replay
        result = crew.replay_task(task_request.task_index)
        
        # Cancel progress monitoring
        progress_task.cancel()
        
        # Update job status to completed
        job_storage[job_id]["status"] = "completed"
        job_storage[job_id]["result"] = result
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 100
        
        # Send final status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "completed",
            "message": "Task replay completed successfully",
            "progress": 100,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Task replay job {job_id} completed successfully")
    
    except Exception as e:
        # Update job status with error
        logger.error(f"Error processing task replay job {job_id}: {str(e)}")
        job_storage[job_id]["status"] = "failed"
        job_storage[job_id]["result"] = {"error": str(e)}
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Send error update via WebSocket
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "failed",
            "message": f"Error: {str(e)}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.post("/train", status_code=202)
async def train_crew(train_request: TrainRequest, background_tasks: BackgroundTasks):
    """Train a crew with multiple iterations"""
    try:
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        # Store job information with training details
        job_storage[job_id] = {
            "job_id": job_id,
            "project_goal": train_request.project_goal,
            "codebase_dir": train_request.codebase_dir,
            "iterations": train_request.iterations,
            "output_file": train_request.output_file,
            "process_type": train_request.process_type,
            "model": train_request.model,
            "memory_enabled": train_request.memory,
            "tools": train_request.tools,
            "status": "queued",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None
        }
        
        # Process the training job in the background
        background_tasks.add_task(process_train_job, job_id, train_request)
        
        # Return job information
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Training session queued successfully",
            "iterations": train_request.iterations,
            "output_file": train_request.output_file
        }
    except Exception as e:
        logger.error(f"Error queuing training session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_train_job(job_id: str, train_request: TrainRequest):
    """Process a training job in the background with real-time updates"""
    try:
        # Update job status
        job_storage[job_id]["status"] = "initializing"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 0
        
        # Send status update via WebSocket
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "initializing",
            "message": "Initializing training session...",
            "progress": 0,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create absolute path for codebase directory
        codebase_path = Path(train_request.codebase_dir).resolve()
        if not codebase_path.exists():
            logger.info(f"Creating directory {codebase_path}")
            codebase_path.mkdir(parents=True, exist_ok=True)
        
        # Update status
        job_storage[job_id]["status"] = "setting_up"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 10
        
        # Send status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "setting_up",
            "message": "Setting up training environment...",
            "progress": 10,
            "timestamp": datetime.now().isoformat()
        })
        
        # Parse CrewAI options
        from crewai import Process
        process_map = {
            "sequential": Process.sequential,
            "parallel": Process.parallel,
            "hierarchical": Process.hierarchical
        }
        process_type = process_map.get(train_request.process_type, Process.hierarchical)
        
        # Parse tools list
        tools_list = None
        if train_request.tools != "all":
            tools_list = [tool.strip() for tool in train_request.tools.split(",")]
            logger.info(f"Using specific tools: {tools_list}")
        
        # Set up training results
        training_results = []
        
        # Update status
        job_storage[job_id]["status"] = "training"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 20
        
        # Send status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "training",
            "message": "Starting training iterations...",
            "progress": 20,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create a progress monitoring task
        progress_task = asyncio.create_task(monitor_progress(job_id))
        
        # Run training iterations
        from .crew import DevTeamCrew
        for i in range(train_request.iterations):
            # Calculate progress percentage
            progress = 20 + int(i / train_request.iterations * 70)
            
            # Update job status
            job_storage[job_id]["status"] = "training"
            job_storage[job_id]["updated_at"] = datetime.now().isoformat()
            job_storage[job_id]["progress"] = progress
            
            # Send iteration update
            await manager.send_update(job_id, {
                "job_id": job_id,
                "status": "training",
                "message": f"Running training iteration {i+1}/{train_request.iterations}...",
                "progress": progress,
                "timestamp": datetime.now().isoformat()
            })
            
            # Run a crew iteration
            crew = DevTeamCrew(
                project_goal=train_request.project_goal,
                codebase_dir=str(codebase_path),
                training_mode=True,
                model=train_request.model or "gpt-4",
                process_type=process_type,
                memory_enabled=train_request.memory,
                tools_list=tools_list
            )
            
            # Run iteration
            result = crew.run()
            
            # Save iteration result
            training_results.append({
                "iteration": i+1,
                "timestamp": datetime.now().isoformat(),
                "result": result
            })
        
        # Cancel progress monitoring
        progress_task.cancel()
        
        # Save training results to file
        output_file_path = os.path.join(codebase_path, train_request.output_file)
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        with open(output_file_path, 'w') as f:
            json.dump({
                "project_goal": train_request.project_goal,
                "iterations": train_request.iterations,
                "model": train_request.model or "gpt-4",
                "process_type": train_request.process_type,
                "results": training_results,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        # Update job status
        job_storage[job_id]["status"] = "completed"
        job_storage[job_id]["result"] = {
            "iterations_completed": train_request.iterations,
            "output_file": output_file_path,
            "summary": training_results
        }
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 100
        
        # Send final status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "completed",
            "message": "Training completed successfully",
            "progress": 100,
            "result": job_storage[job_id]["result"],
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Training job {job_id} completed successfully")
    
    except Exception as e:
        # Update job status with error
        logger.error(f"Error processing training job {job_id}: {str(e)}")
        job_storage[job_id]["status"] = "failed"
        job_storage[job_id]["result"] = {"error": str(e)}
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Send error update via WebSocket
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "failed",
            "message": f"Error: {str(e)}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.post("/test", status_code=202)
async def test_crew(test_request: TestRequest, background_tasks: BackgroundTasks):
    """Test a crew with a specific model"""
    try:
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        # Store job information with test details
        job_storage[job_id] = {
            "job_id": job_id,
            "project_goal": test_request.project_goal,
            "codebase_dir": test_request.codebase_dir,
            "iterations": test_request.iterations,
            "model": test_request.model,
            "process_type": test_request.process_type,
            "memory_enabled": test_request.memory,
            "tools": test_request.tools,
            "status": "queued",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None
        }
        
        # Process the test job in the background
        background_tasks.add_task(process_test_job, job_id, test_request)
        
        # Return job information
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Test session queued successfully",
            "iterations": test_request.iterations,
            "model": test_request.model
        }
    except Exception as e:
        logger.error(f"Error queuing test session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_test_job(job_id: str, test_request: TestRequest):
    """Process a test job in the background with real-time updates"""
    try:
        # Update job status
        job_storage[job_id]["status"] = "initializing"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 0
        
        # Send status update via WebSocket
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "initializing",
            "message": "Initializing test session...",
            "progress": 0,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create absolute path for codebase directory
        codebase_path = Path(test_request.codebase_dir).resolve()
        if not codebase_path.exists():
            logger.info(f"Creating directory {codebase_path}")
            codebase_path.mkdir(parents=True, exist_ok=True)
        
        # Update status
        job_storage[job_id]["status"] = "setting_up"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 10
        
        # Send status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "setting_up",
            "message": "Setting up test environment...",
            "progress": 10,
            "timestamp": datetime.now().isoformat()
        })
        
        # Parse CrewAI options
        from crewai import Process
        process_map = {
            "sequential": Process.sequential,
            "parallel": Process.parallel,
            "hierarchical": Process.hierarchical
        }
        process_type = process_map.get(test_request.process_type, Process.hierarchical)
        
        # Parse tools list
        tools_list = None
        if test_request.tools != "all":
            tools_list = [tool.strip() for tool in test_request.tools.split(",")]
            logger.info(f"Using specific tools: {tools_list}")
        
        # Set up test results
        test_results = []
        
        # Update status
        job_storage[job_id]["status"] = "testing"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 20
        
        # Send status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "testing",
            "message": f"Starting test iterations with model: {test_request.model}...",
            "progress": 20,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create a progress monitoring task
        progress_task = asyncio.create_task(monitor_progress(job_id))
        
        # Run test iterations
        from .crew import DevTeamCrew
        for i in range(test_request.iterations):
            # Calculate progress percentage
            progress = 20 + int(i / test_request.iterations * 70)
            
            # Update job status
            job_storage[job_id]["status"] = "testing"
            job_storage[job_id]["updated_at"] = datetime.now().isoformat()
            job_storage[job_id]["progress"] = progress
            
            # Send iteration update
            await manager.send_update(job_id, {
                "job_id": job_id,
                "status": "testing",
                "message": f"Running test iteration {i+1}/{test_request.iterations}...",
                "progress": progress,
                "timestamp": datetime.now().isoformat()
            })
            
            # Create start time
            start_time = time.time()
            
            # Run a crew iteration
            crew = DevTeamCrew(
                project_goal=test_request.project_goal,
                codebase_dir=str(codebase_path),
                test_mode=True,
                model=test_request.model,
                process_type=process_type,
                memory_enabled=test_request.memory,
                tools_list=tools_list
            )
            
            # Run iteration
            result = crew.run()
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Save iteration result
            test_results.append({
                "iteration": i+1,
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time,
                "result": result
            })
        
        # Cancel progress monitoring
        progress_task.cancel()
        
        # Create results directory
        results_dir = os.path.join(codebase_path, "results", "tests")
        os.makedirs(results_dir, exist_ok=True)
        
        # Save test results to file
        timestamp = int(time.time())
        output_file_path = os.path.join(results_dir, f"test_{test_request.model}_{timestamp}.json")
        
        with open(output_file_path, 'w') as f:
            json.dump({
                "project_goal": test_request.project_goal,
                "iterations": test_request.iterations,
                "model": test_request.model,
                "process_type": test_request.process_type,
                "results": test_results,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        # Update job status
        job_storage[job_id]["status"] = "completed"
        job_storage[job_id]["result"] = {
            "iterations_completed": test_request.iterations,
            "model_tested": test_request.model,
            "output_file": output_file_path,
            "summary": test_results
        }
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        job_storage[job_id]["progress"] = 100
        
        # Send final status update
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "completed",
            "message": "Testing completed successfully",
            "progress": 100,
            "result": job_storage[job_id]["result"],
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Test job {job_id} completed successfully")
    
    except Exception as e:
        # Update job status with error
        logger.error(f"Error processing test job {job_id}: {str(e)}")
        job_storage[job_id]["status"] = "failed"
        job_storage[job_id]["result"] = {"error": str(e)}
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Send error update via WebSocket
        await manager.send_update(job_id, {
            "job_id": job_id,
            "status": "failed",
            "message": f"Error: {str(e)}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.post("/memory/reset", status_code=202)
async def reset_memory(reset_request: MemoryResetRequest):
    """Reset agent memory"""
    try:
        # Reset memory
        from .crew import DevTeamCrew
        
        crew = DevTeamCrew(
            project_goal="Reset memory",
            codebase_dir=".",
            reset_mode=True
        )
        
        result = crew.reset_memory(reset_request.memory_type)
        
        # Return result
        return {
            "status": "success",
            "message": f"{reset_request.memory_type} memory reset successfully",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error resetting memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    """Chat with the Project Manager agent"""
    try:
        # Create Dev Team crew with the current directory
        crew = DevTeamCrew(
            project_goal="Interactive chat session",
            codebase_dir=chat_request.current_dir,
            chat_mode=True,
            model=chat_request.model,
            memory_enabled=chat_request.memory
        )
        
        # Process the chat request
        response = crew.process_chat(
            messages=chat_request.messages,
            model=chat_request.model,
            workspace_context=chat_request.workspace_context
        )
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server"""
    logger.info(f"Starting Dev Team API server on {host}:{port}")
    if reload:
        # Use string-based import for reload support
        uvicorn.run("src.dev_team.server:app", host=host, port=port, reload=reload)
    else:
        # Run the app directly when reload is not needed
        uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # Run the server directly if this script is executed
    run_server()