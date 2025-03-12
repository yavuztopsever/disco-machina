#!/usr/bin/env python
"""
Dev Team Server
--------------
This module implements a FastAPI server that provides RESTful endpoints
for interacting with the Dev Team crew.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
from uuid import uuid4

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query, Body, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import DevTeamCrew
from .crew import DevTeamCrew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Dev Team API",
    description="API for interacting with AI-powered software development crew",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request and response validation
class ProjectRequest(BaseModel):
    project_goal: str = Field(..., description="The goal of the project")
    codebase_dir: str = Field("/tmp/dev_team_output", description="Directory to store code")
    non_interactive: bool = Field(True, description="Whether to run in non-interactive mode")

class TaskRequest(BaseModel):
    task_index: int = Field(..., description="Index of the task to replay")

class ResetMemoryRequest(BaseModel):
    memory_type: str = Field("all", description="Type of memory to reset")
    
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]] = Field(..., description="Chat history messages")
    codebase_dir: str = Field("/tmp/dev_team_output", description="Directory to analyze")
    model: Optional[str] = Field(None, description="Optional model to use for the conversation")

class ProjectResponse(BaseModel):
    job_id: str = Field(..., description="Unique identifier for the job")
    status: str = Field(..., description="Status of the job")
    project_goal: str = Field(..., description="The goal of the project")
    codebase_dir: str = Field(..., description="Directory where code is stored")
    created_at: str = Field(..., description="Timestamp when job was created")

class JobStatusResponse(BaseModel):
    job_id: str = Field(..., description="Unique identifier for the job")
    status: str = Field(..., description="Status of the job")
    project_goal: str = Field(..., description="The goal of the project")
    created_at: str = Field(..., description="Timestamp when job was created")
    updated_at: str = Field(..., description="Timestamp when job was last updated")
    result: Optional[Dict[str, Any]] = Field(None, description="Result of the job if completed")

# In-memory job storage (in production, use a persistent database)
jobs = {}

# Background task function to run the Dev Team crew
async def run_dev_team_task(job_id: str, project_goal: str, codebase_dir: str, non_interactive: bool = True):
    """Run the Dev Team crew as a background task"""
    try:
        # Update job status to running
        jobs[job_id]["status"] = "running"
        jobs[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Create and run the crew
        crew = DevTeamCrew()
        result = crew.run(project_goal, codebase_dir, non_interactive=non_interactive)
        
        # Update job with result
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
        jobs[job_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        # Update job with error
        logger.error(f"Error in job {job_id}: {str(e)}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = {"error": str(e)}
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Root endpoint to check API status"""
    return {
        "status": "online",
        "message": "Dev Team API is running",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectRequest, background_tasks: BackgroundTasks):
    """Create a new project with the Dev Team crew"""
    try:
        # Generate a unique job ID
        job_id = str(uuid4())
        
        # Create job record
        job = {
            "job_id": job_id,
            "status": "queued",
            "project_goal": project.project_goal,
            "codebase_dir": project.codebase_dir,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None
        }
        
        # Store job
        jobs[job_id] = job
        
        # Start background task
        background_tasks.add_task(
            run_dev_team_task,
            job_id=job_id,
            project_goal=project.project_goal,
            codebase_dir=project.codebase_dir,
            non_interactive=project.non_interactive
        )
        
        return job
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")

@app.get("/projects/{job_id}", response_model=JobStatusResponse)
async def get_project_status(job_id: str):
    """Get the status of a project job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return jobs[job_id]

@app.get("/projects", response_model=List[JobStatusResponse])
async def list_projects():
    """List all project jobs"""
    return list(jobs.values())

@app.post("/tasks/replay", status_code=status.HTTP_202_ACCEPTED)
async def replay_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Replay a specific task from the last crew run"""
    try:
        # Generate a unique job ID
        job_id = str(uuid4())
        
        # Create job record
        job = {
            "job_id": job_id,
            "status": "queued",
            "task_index": task_request.task_index,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None
        }
        
        # Store job
        jobs[job_id] = job
        
        # Start background task to replay the task
        background_tasks.add_task(replay_task_background, job_id, task_request.task_index)
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": f"Task replay queued with index {task_request.task_index}"
        }
        
    except Exception as e:
        logger.error(f"Error replaying task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error replaying task: {str(e)}")

async def replay_task_background(job_id: str, task_index: int):
    """Background task to replay a specific task"""
    try:
        # Update job status to running
        jobs[job_id]["status"] = "running"
        jobs[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Create crew and replay task
        crew = DevTeamCrew()
        tasks = crew.get_tasks("Replay task", "replay")
        
        # Validate task index
        if task_index >= len(tasks):
            raise ValueError(f"Invalid task index: {task_index}. Max index is {len(tasks)-1}")
        
        # Replay the task
        task = tasks[task_index]
        result = task.execute()
        
        # Update job with result
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
        jobs[job_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Task replay job {job_id} completed successfully")
        
    except Exception as e:
        # Update job with error
        logger.error(f"Error in task replay job {job_id}: {str(e)}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = {"error": str(e)}
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

@app.post("/memory/reset", status_code=status.HTTP_202_ACCEPTED)
async def reset_memory(request: ResetMemoryRequest):
    """Reset memory of specified type"""
    try:
        crew = DevTeamCrew()
        crew.reset_memories(request.memory_type)
        
        return {
            "status": "success",
            "message": f"Successfully reset {request.memory_type} memories"
        }
        
    except Exception as e:
        logger.error(f"Error resetting memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting memory: {str(e)}")

@app.post("/chat")
async def chat_with_agent(chat_request: ChatRequest):
    """Chat with the Project Manager agent"""
    try:
        # Create a new crew instance
        crew = DevTeamCrew()
        
        # Get the Project Manager agent
        project_manager = crew.get_project_manager_agent()
        
        # Optional model override
        if chat_request.model:
            logger.info(f"Using custom model: {chat_request.model}")
            # This would need to be implemented in your DevTeamCrew class
            crew.set_model(chat_request.model)
        
        # Validate the messages format
        if not chat_request.messages or not isinstance(chat_request.messages, list):
            logger.error("Invalid messages format")
            raise HTTPException(status_code=400, detail="Invalid messages format. Expected a non-empty list.")
            
        # Make sure there's at least one message
        if len(chat_request.messages) == 0:
            logger.error("Empty messages list")
            raise HTTPException(status_code=400, detail="Messages list cannot be empty")
        
        # Check that codebase_dir exists
        if not os.path.exists(chat_request.codebase_dir):
            logger.warning(f"Codebase directory does not exist: {chat_request.codebase_dir}")
            # We'll continue anyway but log the warning
        
        # Process the message with proper error handling
        try:
            logger.info(f"Processing chat request with {len(chat_request.messages)} messages for codebase: {chat_request.codebase_dir}")
            response = project_manager.process_direct_message(
                messages=chat_request.messages,
                codebase_dir=chat_request.codebase_dir
            )
            
            # If response is None or empty, provide a fallback
            if not response:
                response = "I apologize, but I wasn't able to generate a proper response. Please try rephrasing your question."
                
            logger.info(f"Successfully processed chat request")
            
            return {
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as processing_error:
            # Specific error for message processing
            logger.error(f"Error processing message: {str(processing_error)}")
            raise HTTPException(status_code=500, detail=f"Error processing your message: {str(processing_error)}")
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # General error handling
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during chat: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

def start():
    """Start the FastAPI server using uvicorn"""
    import uvicorn
    uvicorn.run("src.dev_team.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()