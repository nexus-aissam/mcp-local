"""
System operation tools for MCP Local
"""

import subprocess
import platform
import os
import json
import psutil
from pathlib import Path
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP

from ..core import ToolBase
from ..core.config import DANGEROUS_COMMANDS, COMMAND_TIMEOUT


class RunCommandTool(ToolBase):
    """Tool for executing shell commands safely"""
    
    def __init__(self):
        super().__init__("run_command", "Execute a shell command and return the output")
    
    def execute(self, command: str) -> str:
        """Execute a shell command with security checks"""
        try:
            # Security: Check for dangerous commands
            if any(cmd in command.lower() for cmd in DANGEROUS_COMMANDS):
                return "Error: Command not allowed for security reasons"
            
            # Additional security checks
            if self._is_command_dangerous(command):
                return "Error: Command contains potentially dangerous operations"
            
            # Execute the command
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=COMMAND_TIMEOUT
            )
            
            # Format output
            output = f"Command: {command}\n"
            output += f"Exit code: {result.returncode}\n"
            
            if result.stdout:
                output += f"Output:\n{result.stdout}\n"
            if result.stderr:
                output += f"Error:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out ({COMMAND_TIMEOUT}s limit)"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def _is_command_dangerous(self, command: str) -> bool:
        """Additional security checks for dangerous command patterns"""
        dangerous_patterns = [
            '>', '>>', '|', '&', ';', '&&', '||',  # Redirection and chaining
            'chmod', 'chown', 'mount', 'umount',   # File permissions
            'kill', 'killall', 'pkill',            # Process killing
            'shutdown', 'reboot', 'halt',          # System control
            'dd', 'fdisk', 'mkfs',                 # Disk operations
            'crontab', 'at',                       # Job scheduling
            'wget', 'curl', 'nc', 'netcat',       # Network tools
        ]
        
        command_lower = command.lower()
        return any(pattern in command_lower for pattern in dangerous_patterns)


class GetSystemInfoTool(ToolBase):
    """Tool for getting comprehensive system information"""
    
    def __init__(self):
        super().__init__("get_system_info", "Get comprehensive system information")
    
    def execute(self) -> str:
        """Get detailed system information"""
        try:
            info = self._collect_system_info()
            return json.dumps(info, indent=2)
        except Exception as e:
            return f"Error getting system info: {str(e)}"
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect comprehensive system information"""
        info = {}
        
        # Basic system info
        info["system"] = {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "hostname": platform.node(),
            "python_version": platform.python_version(),
        }
        
        # Directory information
        info["directories"] = {
            "current": os.getcwd(),
            "home": str(Path.home()),
            "temp": str(Path.home() / "tmp") if (Path.home() / "tmp").exists() else "/tmp",
        }
        
        # CPU information
        try:
            info["cpu"] = {
                "count": psutil.cpu_count(),
                "count_logical": psutil.cpu_count(logical=True),
                "count_physical": psutil.cpu_count(logical=False),
                "usage_percent": psutil.cpu_percent(interval=1),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            }
        except Exception:
            info["cpu"] = {"error": "Unable to get CPU information"}
        
        # Memory information
        try:
            memory = psutil.virtual_memory()
            info["memory"] = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent,
            }
        except Exception:
            info["memory"] = {"error": "Unable to get memory information"}
        
        # Disk information
        try:
            disk = psutil.disk_usage('/')
            info["disk"] = {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round((disk.used / disk.total) * 100, 2),
            }
        except Exception:
            info["disk"] = {"error": "Unable to get disk information"}
        
        # Network information (basic)
        try:
            network_info = psutil.net_if_addrs()
            info["network"] = {
                "interfaces": list(network_info.keys()),
                "interface_count": len(network_info),
            }
        except Exception:
            info["network"] = {"error": "Unable to get network information"}
        
        # Process information
        try:
            info["processes"] = {
                "count": len(psutil.pids()),
                "current_process": {
                    "pid": os.getpid(),
                    "name": psutil.Process().name(),
                    "memory_mb": round(psutil.Process().memory_info().rss / (1024**2), 2),
                }
            }
        except Exception:
            info["processes"] = {"error": "Unable to get process information"}
        
        return info


class GetRunningProcessesTool(ToolBase):
    """Tool for getting information about running processes"""
    
    def __init__(self):
        super().__init__("get_running_processes", "Get information about running processes")
    
    def execute(self, limit: int = 10) -> str:
        """Get information about running processes"""
        try:
            processes = []
            
            # Get all processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage (descending)
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            # Limit results
            processes = processes[:limit]
            
            # Format output
            output = f"Top {limit} processes by CPU usage:\n\n"
            output += f"{'PID':<8} {'NAME':<20} {'CPU%':<8} {'MEM%':<8}\n"
            output += "-" * 50 + "\n"
            
            for proc in processes:
                output += f"{proc['pid']:<8} {proc['name'][:19]:<20} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.1f}\n"
            
            return output
            
        except Exception as e:
            return f"Error getting process information: {str(e)}"


class FindFilesTool(ToolBase):
    """Tool for finding files by pattern"""
    
    def __init__(self):
        super().__init__("find_files", "Find files by pattern in a directory")
    
    def execute(self, pattern: str, directory: str = ".", max_results: int = 50) -> str:
        """Find files matching a pattern"""
        try:
            from pathlib import Path
            import fnmatch
            
            search_path = Path(directory).resolve()
            if not search_path.exists():
                return f"Error: Directory '{directory}' does not exist"
            
            matches = []
            
            # Walk through directory tree
            for root, dirs, files in os.walk(search_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        full_path = Path(root) / file
                        try:
                            stat = full_path.stat()
                            matches.append({
                                'path': str(full_path),
                                'size': stat.st_size,
                                'modified': stat.st_mtime
                            })
                        except:
                            matches.append({
                                'path': str(full_path),
                                'size': 0,
                                'modified': 0
                            })
                
                # Limit results during search to avoid memory issues
                if len(matches) >= max_results:
                    break
            
            # Sort by modification time (newest first)
            matches.sort(key=lambda x: x['modified'], reverse=True)
            
            # Format output
            if not matches:
                return f"No files found matching pattern '{pattern}' in '{directory}'"
            
            output = f"Found {len(matches)} files matching '{pattern}' in '{directory}':\n\n"
            
            for match in matches[:max_results]:
                size_str = self._format_file_size(match['size'])
                output += f"{match['path']} ({size_str})\n"
            
            if len(matches) > max_results:
                output += f"\n... and {len(matches) - max_results} more files"
            
            return output
            
        except Exception as e:
            return f"Error finding files: {str(e)}"
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"


def register_system_tools(mcp: FastMCP):
    """Register system tools with the MCP server"""
    
    # Initialize tool instances
    run_command_tool = RunCommandTool()
    system_info_tool = GetSystemInfoTool()
    processes_tool = GetRunningProcessesTool()
    find_files_tool = FindFilesTool()
    
    @mcp.tool()
    def run_command(command: str) -> str:
        """Execute a shell command and return the output"""
        return run_command_tool.execute(command=command)
    
    @mcp.tool()
    def get_system_info() -> str:
        """Get comprehensive system information"""
        return system_info_tool.execute()
    
    @mcp.tool()
    def get_running_processes(limit: int = 10) -> str:
        """Get information about running processes"""
        return processes_tool.execute(limit=limit)
    
    @mcp.tool()
    def find_files(pattern: str, directory: str = ".", max_results: int = 50) -> str:
        """Find files by pattern in a directory"""
        return find_files_tool.execute(pattern=pattern, directory=directory, max_results=max_results)