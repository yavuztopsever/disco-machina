from typing import List, Dict, Any, Optional
from .dev_tools import (
    CodeAnalysisTool,
    CodeImplementationTool,
    CodeReviewTool,
    RequirementsAnalysisTool,
    TaskTrackingTool,
    TestGenerationTool,
    TestRunnerTool,
    CodeCoverageTool,
    CodeGenerationTool,
    DependencyManagementTool,
    CodebaseAnalysisTool,
    CodeRefactoringTool,
    ObsoleteCodeCleanupTool,
    AgileProjectManagementTool
)
from .crewai_tools import (
    brave_search_tool,
    code_docs_search_tool,
    code_interpreter_tool,
    directory_read_tool,
    file_read_tool,
    file_writer_tool,
    github_search_tool,
    CREWAI_TOOLS
)

# Available tools
__all__ = [
    # Custom tools
    'CodeAnalysisTool',
    'CodeImplementationTool',
    'CodeReviewTool',
    'RequirementsAnalysisTool',
    'TaskTrackingTool',
    'TestGenerationTool',
    'TestRunnerTool',
    'CodeCoverageTool',
    'CodeGenerationTool',
    'DependencyManagementTool',
    'CodebaseAnalysisTool',
    'CodeRefactoringTool',
    'ObsoleteCodeCleanupTool',
    'AgileProjectManagementTool',
    
    # CrewAI tools
    'brave_search_tool',
    'code_docs_search_tool',
    'code_interpreter_tool',
    'directory_read_tool',
    'file_read_tool',
    'file_writer_tool',
    'github_search_tool',
    'CREWAI_TOOLS'
]