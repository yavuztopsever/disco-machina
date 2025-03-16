# DiscoMachina API Documentation

## Overview

The DiscoMachina API provides a comprehensive set of endpoints for interacting with the development team and managing projects, tasks, and chat interactions. This document details all available endpoints, their request/response formats, and usage examples.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API requests require authentication using a Bearer token:

```http
Authorization: Bearer <your_token>
```

## Endpoints

### Projects

#### Create Project

```http
POST /projects
```

**Request Body:**
```json
{
    "name": "string",
    "description": "string",
    "requirements": "string",
    "technologies": ["string"],
    "priority": "high|medium|low"
}
```

**Response:**
```json
{
    "job_id": "string",
    "status": "string",
    "message": "string"
}
```

#### Get Project Status

```http
GET /projects/{job_id}
```

**Response:**
```json
{
    "status": "string",
    "progress": "number",
    "current_task": "string",
    "estimated_completion": "string"
}
```

#### List Projects

```http
GET /projects
```

**Query Parameters:**
- `status`: Filter by status
- `priority`: Filter by priority
- `page`: Page number
- `limit`: Items per page

**Response:**
```json
{
    "projects": [
        {
            "job_id": "string",
            "name": "string",
            "status": "string",
            "progress": "number",
            "created_at": "string"
        }
    ],
    "total": "number",
    "page": "number",
    "pages": "number"
}
```

### Tasks

#### Create Task

```http
POST /tasks
```

**Request Body:**
```json
{
    "project_id": "string",
    "title": "string",
    "description": "string",
    "priority": "high|medium|low",
    "dependencies": ["string"]
}
```

**Response:**
```json
{
    "task_id": "string",
    "status": "string",
    "message": "string"
}
```

#### Get Task Status

```http
GET /tasks/{task_id}
```

**Response:**
```json
{
    "task_id": "string",
    "status": "string",
    "progress": "number",
    "current_step": "string",
    "estimated_completion": "string",
    "dependencies": ["string"],
    "assigned_to": "string"
}
```

#### List Tasks

```http
GET /tasks
```

**Query Parameters:**
- `project_id`: Filter by project
- `status`: Filter by status
- `priority`: Filter by priority
- `page`: Page number
- `limit`: Items per page

**Response:**
```json
{
    "tasks": [
        {
            "task_id": "string",
            "title": "string",
            "status": "string",
            "progress": "number",
            "priority": "string",
            "created_at": "string"
        }
    ],
    "total": "number",
    "page": "number",
    "pages": "number"
}
```

### Memory

#### Store Memory

```http
POST /memory
```

**Request Body:**
```json
{
    "project_id": "string",
    "type": "context|knowledge|decision",
    "content": "string",
    "metadata": {
        "key": "value"
    }
}
```

**Response:**
```json
{
    "memory_id": "string",
    "status": "string",
    "message": "string"
}
```

#### Retrieve Memory

```http
GET /memory/{memory_id}
```

**Response:**
```json
{
    "memory_id": "string",
    "type": "string",
    "content": "string",
    "metadata": {
        "key": "value"
    },
    "created_at": "string",
    "last_accessed": "string"
}
```

#### List Memories

```http
GET /memory
```

**Query Parameters:**
- `project_id`: Filter by project
- `type`: Filter by memory type
- `page`: Page number
- `limit`: Items per page

**Response:**
```json
{
    "memories": [
        {
            "memory_id": "string",
            "type": "string",
            "content": "string",
            "created_at": "string"
        }
    ],
    "total": "number",
    "page": "number",
    "pages": "number"
}
```

### Chat

#### Send Message

```http
POST /chat
```

**Request Body:**
```json
{
    "project_id": "string",
    "message": "string",
    "context": {
        "key": "value"
    }
}
```

**Response:**
```json
{
    "message_id": "string",
    "response": "string",
    "status": "string",
    "context": {
        "key": "value"
    }
}
```

#### Get Chat History

```http
GET /chat/{project_id}
```

**Query Parameters:**
- `page`: Page number
- `limit`: Items per page

**Response:**
```json
{
    "messages": [
        {
            "message_id": "string",
            "role": "user|assistant",
            "content": "string",
            "timestamp": "string",
            "context": {
                "key": "value"
            }
        }
    ],
    "total": "number",
    "page": "number",
    "pages": "number"
}
```

### Development Tools

#### List Available Tools

```http
GET /tools
```

**Response:**
```json
{
    "tools": [
        {
            "tool_id": "string",
            "name": "string",
            "description": "string",
            "parameters": [
                {
                    "name": "string",
                    "type": "string",
                    "required": "boolean",
                    "description": "string"
                }
            ]
        }
    ]
}
```

#### Execute Tool

```http
POST /tools/{tool_id}/execute
```

**Request Body:**
```json
{
    "project_id": "string",
    "parameters": {
        "key": "value"
    }
}
```

**Response:**
```json
{
    "execution_id": "string",
    "status": "string",
    "result": {
        "key": "value"
    },
    "logs": ["string"]
}
```

### System

#### Health Check

```http
GET /health
```

**Response:**
```json
{
    "status": "healthy|degraded|unhealthy",
    "components": {
        "component_name": {
            "status": "string",
            "message": "string"
        }
    },
    "version": "string",
    "uptime": "number"
}
```

#### System Metrics

```http
GET /metrics
```

**Response:**
```json
{
    "cpu_usage": "number",
    "memory_usage": "number",
    "disk_usage": "number",
    "network_usage": {
        "bytes_sent": "number",
        "bytes_received": "number"
    },
    "active_jobs": "number",
    "queue_size": "number"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "error": "string",
    "message": "string",
    "details": {
        "key": "value"
    }
}
```

### 401 Unauthorized
```json
{
    "error": "unauthorized",
    "message": "string"
}
```

### 403 Forbidden
```json
{
    "error": "forbidden",
    "message": "string"
}
```

### 404 Not Found
```json
{
    "error": "not_found",
    "message": "string"
}
```

### 429 Too Many Requests
```json
{
    "error": "rate_limit_exceeded",
    "message": "string",
    "retry_after": "number"
}
```

### 500 Internal Server Error
```json
{
    "error": "internal_server_error",
    "message": "string"
}
```

## Rate Limiting

API requests are limited to:
- 100 requests per minute per IP
- 1000 requests per hour per user
- 10000 requests per day per user

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1623456789
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Events

#### Project Updates
```javascript
{
    "type": "project_update",
    "data": {
        "job_id": "string",
        "status": "string",
        "progress": "number",
        "current_task": "string"
    }
}
```

#### Task Updates
```javascript
{
    "type": "task_update",
    "data": {
        "task_id": "string",
        "status": "string",
        "progress": "number",
        "current_step": "string"
    }
}
```

#### Chat Messages
```javascript
{
    "type": "chat_message",
    "data": {
        "message_id": "string",
        "role": "string",
        "content": "string",
        "timestamp": "string"
    }
}
```

#### System Alerts
```javascript
{
    "type": "system_alert",
    "data": {
        "level": "info|warning|error",
        "message": "string",
        "timestamp": "string"
    }
}
```

## SDK Examples

### Python SDK

```python
from disco_machina import DiscoMachina

# Initialize client
client = DiscoMachina(api_key="your_api_key")

# Create project
project = client.create_project(
    name="My Project",
    description="Project description",
    requirements="Project requirements",
    technologies=["Python", "FastAPI"],
    priority="high"
)

# Get project status
status = client.get_project_status(project.job_id)

# Create task
task = client.create_task(
    project_id=project.job_id,
    title="Implement feature",
    description="Feature description",
    priority="high"
)

# Send chat message
response = client.send_chat_message(
    project_id=project.job_id,
    message="How do I implement this feature?"
)
```

### JavaScript SDK

```javascript
const { DiscoMachina } = require('disco-machina');

// Initialize client
const client = new DiscoMachina({
    apiKey: 'your_api_key'
});

// Create project
const project = await client.createProject({
    name: 'My Project',
    description: 'Project description',
    requirements: 'Project requirements',
    technologies: ['JavaScript', 'Node.js'],
    priority: 'high'
});

// Get project status
const status = await client.getProjectStatus(project.jobId);

// Create task
const task = await client.createTask({
    projectId: project.jobId,
    title: 'Implement feature',
    description: 'Feature description',
    priority: 'high'
});

// Send chat message
const response = await client.sendChatMessage({
    projectId: project.jobId,
    message: 'How do I implement this feature?'
});
```

## Best Practices

1. **Error Handling**
   - Always check response status codes
   - Implement proper error handling for all API calls
   - Use exponential backoff for retries

2. **Rate Limiting**
   - Monitor rate limit headers
   - Implement rate limiting on the client side
   - Use WebSocket for real-time updates

3. **Authentication**
   - Store API keys securely
   - Rotate API keys regularly
   - Use environment variables for sensitive data

4. **Performance**
   - Use pagination for large datasets
   - Implement caching where appropriate
   - Use WebSocket for real-time updates

5. **Security**
   - Use HTTPS for all API calls
   - Validate all input data
   - Sanitize output data
   - Follow OWASP security guidelines 