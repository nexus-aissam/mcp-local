"""
Tools module for MCP Local

This module contains all the tool implementations for the MCP Local server.
Tools are organized by functionality:
- file_operations: Basic file I/O operations
- file_editing: Advanced file editing capabilities
- search_tools: Search and replace functionality
- system_tools: System operations and information gathering
"""

from .file_operations import register_file_operations
from .file_editing import register_file_editing_tools
from .search_tools import register_search_tools
from .system_tools import register_system_tools

__all__ = [
    "register_file_operations",
    "register_file_editing_tools", 
    "register_search_tools",
    "register_system_tools"
]
