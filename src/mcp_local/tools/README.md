# System Tools Documentation

## New System Operation Tools

### 🖥️ System Information & Control
- **System Information**: Comprehensive hardware and software details
- **Process Management**: View and monitor running processes
- **Command Execution**: Safe execution of shell commands with security restrictions
- **File Discovery**: Advanced file finding with pattern matching

## Available System Tools

### System Information Tools
- `get_system_info()` - Get comprehensive system information including:
  - Operating system details and version
  - Hardware specifications (CPU, memory, disk)
  - Python environment information
  - Directory paths and network interfaces
  - Current process information

### Process Management Tools
- `get_running_processes(limit)` - View running processes with:
  - Process ID (PID) and name
  - CPU usage percentage
  - Memory usage percentage
  - Sorted by CPU usage (highest first)
  - Configurable result limit (default: 10)

### Command Execution Tools
- `run_command(command)` - Execute shell commands safely with:
  - **Security restrictions**: Blocks dangerous commands (rm, sudo, etc.)
  - **Pattern detection**: Prevents dangerous command patterns
  - **Timeout protection**: 30-second execution limit
  - **Detailed output**: Exit code, stdout, and stderr
  - **Error handling**: Graceful error reporting

### File Discovery Tools
- `find_files(pattern, directory, max_results)` - Find files by pattern with:
  - **Glob pattern matching**: Support for wildcards (*, ?, [])
  - **Recursive search**: Searches subdirectories
  - **Size and date info**: File size and modification time
  - **Result limiting**: Prevents memory issues with large results
  - **Hidden file filtering**: Skips hidden directories

## Security Features

### Command Execution Security
- **Blocked Commands**: rm, del, format, sudo, su, passwd, chmod, chown, etc.
- **Pattern Detection**: Prevents redirection, chaining, and dangerous operations
- **Timeout Protection**: Commands are terminated after 30 seconds
- **Access Control**: No privilege escalation allowed

### File System Security
- **Path Validation**: Prevents directory traversal attacks
- **Size Limits**: Protects against memory exhaustion
- **Hidden File Filtering**: Skips system and hidden directories
- **Permission Checking**: Respects file system permissions

## Usage Examples

### Get System Information
```python
# Get comprehensive system information
system_info = get_system_info()
```

### Monitor Processes
```python
# Get top 10 processes by CPU usage
processes = get_running_processes(limit=10)

# Get top 20 processes
processes = get_running_processes(limit=20)
```

### Execute Commands Safely
```python
# List files
result = run_command("ls -la")

# Check disk usage
result = run_command("df -h")

# Get system uptime
result = run_command("uptime")

# Note: Dangerous commands are blocked
result = run_command("rm -rf /")  # This will be blocked
```

### Find Files
```python
# Find all Python files
files = find_files("*.py", "/path/to/search")

# Find configuration files
files = find_files("*.conf", "/etc", max_results=100)

# Find files with specific pattern
files = find_files("test_*.py", ".", max_results=25)
```

## Error Handling

All system tools include comprehensive error handling:
- **Command Security**: Blocked commands return security error messages
- **Timeout Handling**: Long-running commands are terminated gracefully
- **Permission Errors**: File system access errors are handled gracefully
- **Resource Limits**: Memory and processing limits prevent system overload
- **Exception Handling**: All exceptions are caught and returned as error messages

## Configuration

System tools respect the configuration settings in `core/config.py`:
- `DANGEROUS_COMMANDS`: List of blocked command patterns
- `COMMAND_TIMEOUT`: Maximum execution time for commands (30 seconds)
- `MAX_FILE_SIZE`: Maximum file size for operations (1MB)

## Integration with Existing Architecture

The system tools integrate seamlessly with the existing MCP Local architecture:
- **Base Classes**: Inherit from `ToolBase` for consistency
- **Error Handling**: Use the same exception handling patterns
- **Security**: Follow the same security principles as file operations
- **Logging**: Compatible with the existing history and logging system
- **Configuration**: Use the same configuration management system

## Performance Considerations

- **Process Monitoring**: CPU and memory usage is sampled efficiently
- **File Discovery**: Results are limited to prevent memory issues
- **Command Execution**: Timeout protection prevents hanging processes
- **Resource Management**: System information gathering is optimized for speed

## Future Enhancements

Planned improvements for system tools:
- **Process Filtering**: Filter processes by name, CPU, or memory usage
- **System Monitoring**: Real-time system resource monitoring
- **Service Management**: Safe service start/stop operations
- **Network Tools**: Network connectivity and interface management
- **Log Analysis**: System log parsing and analysis tools