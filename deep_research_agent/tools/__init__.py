"""
Tools package for Deep Research Agent
Contains web search and academic search tools
"""

from .web_search import WebSearchTool
from .acad_search import AcademicSearchTool

__all__ = [
    'WebSearchTool',
    'AcademicSearchTool'
]

# Tool factory function for easy instantiation
def create_web_search_tool(api_key=None):
    """Create a web search tool instance"""
    return WebSearchTool(api_key=api_key)

def create_academic_search_tool(pubmed_api_key=None):
    """Create an academic search tool instance"""
    return AcademicSearchTool(pubmed_api_key=pubmed_api_key)

# Tool validation utilities
def validate_all_tools():
    """Validate all tools are properly configured"""
    web_tool = WebSearchTool()
    acad_tool = AcademicSearchTool()
    
    return {
        "web_search": web_tool.validate_api_key(),
        "academic_search": True  # ArXiv doesn't require API key
    } 