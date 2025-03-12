"""
CrewAI tools integration for Dev Team.

This module provides access to built-in CrewAI tools:
- BraveSearchTool: For web search functionality
- CodeDocsSearchTool: For RAG search in code documentation
- CodeInterpreterTool: For safe code execution
- DirectoryReadTool: For exploring directory structures
- FileReadTool: For reading file contents
- FileWriterTool: For writing files
- GithubSearchTool: For searching GitHub repositories
"""

# Import built-in CrewAI tools
from crewai_tools import (
    BraveSearchTool,
    CodeDocsSearchTool,
    CodeInterpreterTool,
    DirectoryReadTool,
    FileReadTool,
    FileWriterTool,
    GithubSearchTool
)
from crewai.tools import BaseTool

# Create tool instances - these will be used directly in the agents.yaml config
# Initialize tools with proper error handling

# For BraveSearchTool, we need to handle the case when BRAVE_API_KEY is not set
try:
    brave_search_tool = BraveSearchTool(
        country="US",
        n_results=5,
        save_file=True
    )
except ValueError:
    # Create a placeholder if API key is missing
    print("Warning: BRAVE_API_KEY not set. BraveSearchTool will be initialized as a placeholder.")
    # We'll create a dummy class that logs when it's used
    class DummyBraveSearchTool(BaseTool):
        name: str = "BraveSearch Tool (DISABLED)"
        description: str = "Search the internet using Brave Search (REQUIRES API KEY)"
        
        def _run(self, search_query: str) -> str:
            return f"BraveSearchTool is disabled. Please set BRAVE_API_KEY environment variable to use this tool."
            
    brave_search_tool = DummyBraveSearchTool()

code_docs_search_tool = CodeDocsSearchTool()

code_interpreter_tool = CodeInterpreterTool()

directory_read_tool = DirectoryReadTool()

file_read_tool = FileReadTool()

file_writer_tool = FileWriterTool()

# For GithubSearchTool, we need to handle the case when GH_TOKEN is not set
try:
    github_search_tool = GithubSearchTool(
        content_types=["code", "repo", "pr", "issue"]
    )
except ValueError:
    # Create a placeholder if API key is missing
    print("Warning: GH_TOKEN not set. GithubSearchTool will be initialized as a placeholder.")
    # We'll create a dummy class that logs when it's used
    class DummyGithubSearchTool(BaseTool):
        name: str = "GitHub Search Tool (DISABLED)"
        description: str = "Search GitHub repositories (REQUIRES API KEY)"
        
        def _run(self, search_query: str) -> str:
            return f"GithubSearchTool is disabled. Please set GH_TOKEN environment variable to use this tool."
            
    github_search_tool = DummyGithubSearchTool()

# Dictionary mapping tool names to instances
CREWAI_TOOLS = {
    "BraveSearchTool": brave_search_tool,
    "CodeDocsSearchTool": code_docs_search_tool, 
    "CodeInterpreterTool": code_interpreter_tool,
    "DirectoryReadTool": directory_read_tool,
    "FileReadTool": file_read_tool,
    "FileWriterTool": file_writer_tool,
    "GithubSearchTool": github_search_tool
}