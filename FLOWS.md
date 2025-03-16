# DiscoMachina System Flows

This document outlines the key workflow processes in the DiscoMachina system, describing how data and control flow through the system's components.

## Main Flow - Working Directory Based Operation

The primary workflow for DiscoMachina is designed to be simple and intuitive, working directly within the user's current codebase:

```mermaid
sequenceDiagram
    participant User
    participant Terminal as Terminal
    participant Client as DiscoMachina Client
    participant Server as API Server
    participant Crew as Dev Team Crew
    participant Agents as AI Agents
    
    User->>Terminal: cd /path/to/codebase
    User->>Terminal: discomachina chat
    Terminal->>Client: Launch with current directory
    Client->>Client: Analyze workspace context
    Client->>Server: Connect with codebase path
    Server->>Server: Initialize session
    Server->>Crew: Create agents with codebase context
    
    loop Chat Interaction
        User->>Client: Ask question or give task
        Client->>Server: Send request with context
        Server->>Crew: Process request
        Crew->>Agents: Delegate to appropriate agent
        Agents->>Agents: Work within codebase
        Agents->>Crew: Return results
        Crew->>Server: Format response
        Server->>Client: Send response
        Client->>User: Display results
    end
```

With this flow:
1. The user navigates to their project directory in the terminal
2. The DiscoMachina client automatically uses the current directory as the working context
3. All operations are contained within this codebase, ensuring isolation and safety
4. No additional setup or configuration is needed - "it just works"

## Core Flows

### 1. Terminal Client to API Server Flow

```mermaid
sequenceDiagram
    participant User
    participant Terminal as Terminal Client
    participant Server as API Server
    participant Crew as Dev Team Crew
    participant Agents as AI Agents
    
    User->>Terminal: Enter Command
    Terminal->>Terminal: Parse and Validate
    Terminal->>Terminal: Get Current Directory
    Terminal->>Server: Send API Request with Directory
    Server->>Server: Authenticate & Validate
    Server->>Crew: Process Request in Context
    Crew->>Agents: Delegate Tasks
    Agents->>Agents: Execute Tasks within Directory
    Agents->>Crew: Return Results
    Crew->>Server: Update Job Status
    Server->>Terminal: WebSocket Real-time Response
    Terminal->>User: Display Results
```

### 2. Project Creation Flow

```mermaid
sequenceDiagram
    participant User
    participant Terminal as Terminal Client
    participant Server as API Server
    participant WSManager as WebSocket Manager
    participant Crew as Dev Team Crew
    
    User->>Terminal: cd /path/to/codebase
    User->>Terminal: discomachina create --goal "..." 
    Terminal->>Terminal: Get Current Directory
    Terminal->>Server: POST /projects with CrewAI options
    Server->>Server: Generate Job ID
    Server->>Terminal: Return Job ID
    Terminal->>WSManager: Open WebSocket Connection
    Terminal->>Terminal: Display Progress Bar
    WSManager->>Terminal: Send Real-time Updates
    Server->>Crew: Initialize Dev Team with Process Type
    Crew->>Crew: Configure Agents with Memory & Delegation
    Crew->>Crew: Apply Tool Selection
    Crew->>Crew: Execute Tasks in Dependency Order
    Crew->>Server: Send Checkpoints & Updates
    Server->>WSManager: Broadcast Status Updates
    WSManager->>Terminal: Send Status Updates
    Crew->>Server: Send Completion Status
    Server->>WSManager: Send Final Results
    WSManager->>Terminal: Receive Results
    Terminal->>User: Display Project Results
```

### 3. Agent Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant Client as Terminal Client
    participant Crew as Crew Manager
    participant PM as Project Manager
    participant SA as Software Architect
    participant FD as Fullstack Developer
    participant TE as Test Engineer
    participant Tools as Built-in & Custom Tools
    
    User->>Client: Start CrewAI Process
    Client->>Crew: Initialize with Process Type
    Note over Crew: Hierarchical Process
    
    Crew->>PM: Assign Leadership Role
    PM->>PM: Analyze Requirements with Memory
    PM->>SA: Delegate Architecture Task
    
    SA->>SA: Design Architecture
    SA->>SA: Analyze Codebase
    SA->>Tools: Use CodeAnalysisTool
    SA->>Tools: Use CodebaseAnalysisTool
    SA->>FD: Delegate Implementation Task
    
    FD->>FD: Implement Features
    FD->>Tools: Use CodeImplementationTool
    FD->>Tools: Use CodeGenerationTool
    FD->>Tools: Use BraveSearchTool
    FD->>TE: Delegate Testing Task
    
    TE->>TE: Develop Tests
    TE->>Tools: Use TestGenerationTool
    TE->>Tools: Use CodeCoverageTool
    TE->>Tools: Use CodeReviewTool
    TE->>SA: Report Code Issues
    
    SA->>SA: Refactor Code
    SA->>Tools: Use CodeRefactoringTool
    SA->>PM: Report Completion
    
    PM->>PM: Update Documentation
    PM->>Crew: Return Aggregated Results
    Crew->>Client: Return Final Output
    Client->>User: Display Results with Progress
```

### 4. Task Execution Flow

```mermaid
graph TD
    A[Start Sprint] -->|Initialize| B[Requirements Analysis]
    B -->|Requirements Defined| C[Architecture Design]
    C -->|Architecture Ready| D[Codebase Analysis]
    D -->|Analysis Complete| E[Sprint Planning]
    E -->|Plan Created| F[Feature Implementation]
    F -->|Features Implemented| G[Test Development]
    G -->|Tests Created| H[Code Review]
    H -->|Review Complete| I[Code Refactoring]
    I -->|Code Refactored| J[Code Cleanup]
    J -->|Cleanup Complete| K[Documentation Update]
    K -->|Docs Updated| L[Sprint Retrospective]
    L -->|Sprint Complete| M[End Sprint]
```

## Advanced Flows

### 5. Context Management Flow

```mermaid
graph TD
    A[New Message] -->|Add to Context| B[Context Storage]
    B -->|Check Size| C{Size > Threshold?}
    C -->|Yes| D[Context Compaction]
    C -->|No| E[Continue Processing]
    D -->|Summarize Old Messages| F[Create Summary]
    F -->|Replace Old Messages| G[Compact Context]
    G -->|Reset Token Count| E
    E -->|Process| H[Message Handler]
```

### 6. Tool Execution Flow

```mermaid
sequenceDiagram
    participant Agent
    participant ToolManager
    participant Tool
    participant System
    
    Agent->>ToolManager: Request Tool Execution
    ToolManager->>ToolManager: Validate Tool Request
    ToolManager->>Tool: Initialize Tool
    Tool->>System: Execute System Operation
    System->>Tool: Return Result
    Tool->>ToolManager: Process Result
    ToolManager->>Agent: Return Formatted Result
```

### 7. Error Recovery Flow

```mermaid
graph TD
    A[Operation] -->|Execute| B{Error Detected?}
    B -->|Yes| C[Determine Error Type]
    B -->|No| D[Continue Normal Flow]
    
    C -->|Network Error| E[Retry with Backoff]
    C -->|API Error| F[Use Fallback]
    C -->|System Error| G[Execute Recovery]
    
    E -->|Retry Success| D
    E -->|Max Retries| H[Report Failure]
    
    F -->|Fallback Success| D
    F -->|Fallback Failed| H
    
    G -->|Recovery Success| D
    G -->|Recovery Failed| H
    
    H -->|Log Error| I[Notify User]
    I -->|Guidance| J[Suggest Mitigation]
```

### 8. Offline Mode Flow

```mermaid
graph TD
    A[Client Request] -->|Check Connection| B{Server Available?}
    B -->|Yes| C[Online Mode]
    B -->|No| D[Offline Mode]
    
    C -->|Send Request| E[API Server]
    E -->|Process| F[Return Response]
    F -->|Cache| G[Update Cache]
    G -->|Display| H[Show Response]
    
    D -->|Check Cache| I{Cache Hit?}
    I -->|Yes| J[Retrieve Cached Response]
    I -->|No| K[Generate Limited Response]
    
    J -->|Display| H
    K -->|Display| H
    H -->|User| L[User Views Response]
```

### 9. Working Directory Chat Flow

```mermaid
sequenceDiagram
    participant User
    participant Terminal
    participant Client as DiscoMachina Client
    participant Server
    participant Crew as Dev Team Crew
    participant Manager as Project Manager Agent
    
    User->>Terminal: cd /path/to/project
    User->>Terminal: discomachina chat
    Terminal->>Client: Launch with current directory
    Client->>Client: Analyze workspace context
    Client->>Client: Scan for config files, dirs, code
    
    Client->>Server: POST /chat with workspace context
    Server->>Crew: Initialize chat mode with codebase
    Crew->>Manager: Initialize with memory & context
    Server->>Client: Return connection status
    Client->>User: Show welcome & workspace info
    
    loop Chat Interaction
        User->>Client: Ask question or request task
        alt Special Command
            Client->>Client: Handle command (/help, /status, etc.)
        else Normal Message
            Client->>Client: Add message to history
            Client->>Server: POST /chat with context & history
            Server->>Crew: Process in codebase context
            Crew->>Manager: Generate response with memory
            Manager->>Crew: Return formatted response
            Crew->>Server: Return response
            Server->>Client: Send response
            Client->>User: Display colored response
            Client->>Client: Update history & compact if needed
        end
    end
    
    User->>Client: Exit chat ("exit" or Ctrl+C)
    Client->>Client: Save chat history
    Client->>User: Show goodbye message
```

### 10. CrewAI Training and Testing Flow

```mermaid
sequenceDiagram
    participant User
    participant Terminal
    participant Server
    participant WSManager as WebSocket Manager
    participant Crew as Dev Team Crew
    
    alt Train Mode
        User->>Terminal: discomachina train <iterations> <output> --goal "..."
        Terminal->>Server: POST /train with options
    else Test Mode
        User->>Terminal: discomachina test <iterations> <model> --goal "..."
        Terminal->>Server: POST /test with options
    end
    
    Server->>Server: Generate Job ID
    Server->>Terminal: Return Job ID
    Terminal->>WSManager: Open WebSocket Connection
    
    alt Train Mode
        Server->>Server: Set up training environment
        loop For each iteration
            Server->>Crew: Create new crew with memory
            Crew->>Crew: Run full workflow
            Crew->>Server: Return iteration results
            Server->>WSManager: Send progress update
            WSManager->>Terminal: Update progress bar
        end
        Server->>Server: Save training results to file
    else Test Mode
        Server->>Server: Set up testing environment
        loop For each iteration
            Server->>Crew: Create new crew with test model
            Server->>Server: Start performance timer
            Crew->>Crew: Run full workflow
            Server->>Server: Calculate execution metrics
            Crew->>Server: Return iteration results
            Server->>WSManager: Send progress update
            WSManager->>Terminal: Update progress bar
        end
        Server->>Server: Save test results to file
    end
    
    Server->>WSManager: Send completion status
    WSManager->>Terminal: Receive final results
    Terminal->>User: Display summary & metrics
```

### 10. Job Monitoring Flow

```mermaid
graph TD
    A[Start Job] -->|Create Job| B[Store in Job Storage]
    B -->|Return Job ID| C[Client Monitoring]
    
    C -->|Poll Status| D[Check Job Status]
    D -->|Still Running| E[Update Progress]
    D -->|Completed| F[Fetch Results]
    D -->|Failed| G[Get Error Details]
    
    E -->|Wait Interval| C
    F -->|Display| H[Show Success]
    G -->|Display| I[Show Error]
```

## Implementation Status

The following enhancements have been implemented to improve the DiscoMachina system:

✅ **Working Directory Based Operation**: System now automatically uses the current directory as working context
✅ **WebSocket for real-time updates**: Replaced polling with WebSocket connections for real-time job status updates
✅ **Checkpointing for long-running tasks**: Added task checkpointing for resilience against interruptions
✅ **Enhanced error recovery**: Implemented exponential backoff retries for network and API errors
✅ **Improved context management**: Enhanced context handling with better compaction strategies
✅ **Expanded CrewAI integration**: Added support for all CrewAI process types, memory, and delegation options
✅ **Enhanced tools integration**: Added support for both custom and built-in CrewAI tools
✅ **Training and testing capabilities**: Added support for training iterations and model testing

### Future Improvements

1. **Expand offline capabilities**: Cache more interactions and enable better offline functionality
2. **Implement proper authentication flow**: Add token-based authentication with refresh capabilities
3. **Add session persistence**: Allow users to resume sessions across client restarts
4. **Create better tool discovery mechanism**: Add dynamic tool discovery and registration
5. **Add support for multi-project workspaces**: Allow managing multiple projects simultaneously
6. **Implement user preferences**: Add support for user-specific preferences and settings