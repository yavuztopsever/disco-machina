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
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
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

class ProjectRequest(BaseModel):
    """Project creation request model"""
    project_goal: str = Field(..., description="Goal of the project")
    codebase_dir: str = Field(..., description="Directory containing the codebase")
    non_interactive: bool = Field(False, description="Whether to run in non-interactive mode")

class ChatRequest(BaseModel):
    """Chat request model"""
    messages: List[Dict[str, str]] = Field(..., description="Chat messages")
    model: str = Field("default", description="Model to use for the chat")
    workspace_context: Dict[str, Any] = Field({}, description="Context about the workspace")

class TaskReplayRequest(BaseModel):
    """Task replay request model"""
    task_index: int = Field(..., description="Index of the task to replay")

class MemoryResetRequest(BaseModel):
    """Memory reset request model"""
    memory_type: str = Field("all", description="Type of memory to reset")

async def process_job(job_id: str, project_request: ProjectRequest):
    """Process a job in the background"""
    try:
        # Update job status
        job_storage[job_id]["status"] = "running"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Run the Dev Team
        from .crew import DevTeamCrew
        
        # Create absolute path for codebase directory
        codebase_path = Path(project_request.codebase_dir).resolve()
        if not codebase_path.exists():
            logger.info(f"Creating directory {codebase_path}")
            codebase_path.mkdir(parents=True, exist_ok=True)
        
        # Create Dev Team crew
        logger.info(f"Creating Dev Team crew for project: {project_request.project_goal}")
        logger.info(f"Using codebase directory: {codebase_path}")
        
        crew = DevTeamCrew(
            project_goal=project_request.project_goal,
            codebase_dir=str(codebase_path),
            interactive=not project_request.non_interactive
        )
        
        # Run the crew
        logger.info("Starting Dev Team crew...")
        result = crew.run()
        
        # Update job status
        job_storage[job_id]["status"] = "completed"
        job_storage[job_id]["result"] = result
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Job {job_id} completed successfully")
    
    except Exception as e:
        # Update job status with error
        logger.error(f"Error processing job {job_id}: {str(e)}")
        job_storage[job_id]["status"] = "failed"
        job_storage[job_id]["result"] = {"error": str(e)}
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

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
    """Replay a task"""
    try:
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        # Store job information
        job_storage[job_id] = {
            "job_id": job_id,
            "task_index": task_request.task_index,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None
        }
        
        # Process the task replay in the background
        background_tasks.add_task(replay_task_job, job_id, task_request.task_index)
        
        # Return job information
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Task replay queued successfully"
        }
    except Exception as e:
        logger.error(f"Error queuing task replay: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def replay_task_job(job_id: str, task_index: int):
    """Process a task replay job in the background"""
    try:
        # Update job status
        job_storage[job_id]["status"] = "running"
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Run task replay
        from .crew import DevTeamCrew
        
        crew = DevTeamCrew(
            project_goal="Replay task",
            codebase_dir=".",
            replay_mode=True
        )
        
        result = crew.replay_task(task_index)
        
        # Update job status
        job_storage[job_id]["status"] = "completed"
        job_storage[job_id]["result"] = result
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Task replay job {job_id} completed successfully")
    
    except Exception as e:
        # Update job status with error
        logger.error(f"Error processing task replay job {job_id}: {str(e)}")
        job_storage[job_id]["status"] = "failed"
        job_storage[job_id]["result"] = {"error": str(e)}
        job_storage[job_id]["updated_at"] = datetime.now().isoformat()

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
        # Process chat request
        from .crew import DevTeamCrew
        
        # Extract workspace context
        workspace_context = chat_request.workspace_context
        
        # Create Dev Team crew with chat mode
        crew = DevTeamCrew(
            project_goal="Chat session",
            codebase_dir=workspace_context.get("path", "."),
            chat_mode=True
        )
        
        # Process chat message
        response = crew.process_chat(
            messages=chat_request.messages,
            model=chat_request.model,
            workspace_context=workspace_context
        )
        
        # Return response
        return {
            "response": response
        }
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server"""
    logger.info(f"Starting Dev Team API server on {host}:{port}")
    try:
        # Try to run the app directly
        uvicorn.run(app, host=host, port=port, reload=reload)
    except Exception as e:
        logger.error(f"Error running server with direct import: {str(e)}")
        # Fall back to string-based import
        uvicorn.run("src.dev_team.server:app", host=host, port=port, reload=reload)

if __name__ == "__main__":
    # Run the server directly if this script is executed
    run_server()