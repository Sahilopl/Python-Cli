"""
Python-Based Command Terminal with Web Interface
A terminal interface that mimics real system terminals with Flask backend.
"""

from flask import Flask, render_template, request, jsonify
import os
import subprocess
import psutil
import json
import shlex
import platform
from datetime import datetime
import re
from pathlib import Path

app = Flask(__name__)

class CommandTerminal:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.command_history = []
        self.system_info = self.get_system_info()
        
    def get_system_info(self):
        """Get basic system information"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def get_current_directory(self):
        """Get current working directory"""
        return self.current_dir
    
    def change_directory(self, path):
        """Change current directory"""
        try:
            if path == "..":
                new_path = os.path.dirname(self.current_dir)
            elif path == "~":
                new_path = os.path.expanduser("~")
            elif os.path.isabs(path):
                new_path = path
            else:
                new_path = os.path.join(self.current_dir, path)
            
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_dir = os.path.abspath(new_path)
                return f"Changed directory to: {self.current_dir}"
            else:
                return f"Error: Directory '{path}' not found"
        except Exception as e:
            return f"Error changing directory: {str(e)}"
    
    def list_directory(self, path=None):
        """List directory contents"""
        try:
            target_dir = path if path else self.current_dir
            if not os.path.isabs(target_dir):
                target_dir = os.path.join(self.current_dir, target_dir)
            
            if not os.path.exists(target_dir):
                return f"Error: Directory '{target_dir}' not found"
            
            items = []
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                is_dir = os.path.isdir(item_path)
                size = os.path.getsize(item_path) if not is_dir else 0
                modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M')
                
                items.append({
                    'name': item,
                    'type': 'directory' if is_dir else 'file',
                    'size': size,
                    'modified': modified
                })
            
            return items
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def create_directory(self, dirname):
        """Create a new directory"""
        try:
            if not os.path.isabs(dirname):
                dirname = os.path.join(self.current_dir, dirname)
            
            os.makedirs(dirname, exist_ok=True)
            return f"Directory '{dirname}' created successfully"
        except Exception as e:
            return f"Error creating directory: {str(e)}"
    
    def remove_item(self, item_name):
        """Remove file or directory"""
        try:
            if not os.path.isabs(item_name):
                item_path = os.path.join(self.current_dir, item_name)
            else:
                item_path = item_name
            
            if not os.path.exists(item_path):
                return f"Error: '{item_name}' not found"
            
            if os.path.isdir(item_path):
                os.rmdir(item_path)
                return f"Directory '{item_name}' removed successfully"
            else:
                os.remove(item_path)
                return f"File '{item_name}' removed successfully"
        except Exception as e:
            return f"Error removing '{item_name}': {str(e)}"
    
    def get_system_monitoring(self):
        """Get system monitoring information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get top processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage and get top 5
            processes = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:5]
            
            return {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': round(memory.total / (1024**3), 2),
                    'available': round(memory.available / (1024**3), 2),
                    'percent': memory.percent,
                    'used': round(memory.used / (1024**3), 2)
                },
                'disk': {
                    'total': round(disk.total / (1024**3), 2),
                    'used': round(disk.used / (1024**3), 2),
                    'free': round(disk.free / (1024**3), 2),
                    'percent': round((disk.used / disk.total) * 100, 2)
                },
                'top_processes': processes
            }
        except Exception as e:
            return f"Error getting system information: {str(e)}"
    
    def execute_system_command(self, command):
        """Execute system commands safely"""
        try:
            # Restricted commands for security
            dangerous_commands = ['rm -rf', 'format', 'del /f', 'shutdown', 'reboot']
            if any(danger in command.lower() for danger in dangerous_commands):
                return "Error: Command not allowed for security reasons"
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.current_dir,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nError: {result.stderr}"
            
            return output if output else "Command executed successfully"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def parse_natural_language(self, command):
        """Basic natural language processing for commands"""
        command = command.lower().strip()
        
        # Create folder patterns
        create_folder_patterns = [
            r'create (?:folder|directory) (\w+)',
            r'make (?:folder|directory) (\w+)',
            r'mkdir (\w+)'
        ]
        
        # Move file patterns
        move_file_patterns = [
            r'move (?:file )?(\w+(?:\.\w+)?) to (\w+)',
            r'mv (\w+(?:\.\w+)?) (\w+)'
        ]
        
        # List patterns
        list_patterns = [
            r'list (?:files|directory|contents)',
            r'show (?:files|directory|contents)',
            r'ls'
        ]
        
        # Change directory patterns
        cd_patterns = [
            r'(?:go to|change to|cd) (\w+)',
            r'enter (?:directory|folder) (\w+)'
        ]
        
        # Check patterns and return appropriate command
        for pattern in create_folder_patterns:
            match = re.search(pattern, command)
            if match:
                return f"mkdir {match.group(1)}"
        
        for pattern in move_file_patterns:
            match = re.search(pattern, command)
            if match:
                return f"mv {match.group(1)} {match.group(2)}"
        
        for pattern in list_patterns:
            if re.search(pattern, command):
                return "ls"
        
        for pattern in cd_patterns:
            match = re.search(pattern, command)
            if match:
                return f"cd {match.group(1)}"
        
        return None
    
    def execute_command(self, command):
        """Main command execution function"""
        original_command = command
        command = command.strip()
        
        # Add to history
        self.command_history.append({
            'command': command,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Keep only last 50 commands
        if len(self.command_history) > 50:
            self.command_history = self.command_history[-50:]
        
        if not command:
            return "No command entered"
        
        # Try natural language processing first
        parsed_command = self.parse_natural_language(command)
        if parsed_command:
            command = parsed_command
        
        # Split command into parts
        parts = command.split()
        cmd = parts[0].lower()
        
        # Handle built-in commands
        if cmd == 'pwd':
            return self.current_dir
        
        elif cmd == 'cd':
            if len(parts) > 1:
                return self.change_directory(parts[1])
            else:
                return self.change_directory(os.path.expanduser("~"))
        
        elif cmd == 'ls' or cmd == 'dir':
            if len(parts) > 1:
                result = self.list_directory(parts[1])
            else:
                result = self.list_directory()
            
            if isinstance(result, list):
                # Format the output
                output = f"Contents of {self.current_dir}:\n\n"
                output += f"{'Name':<30} {'Type':<10} {'Size':<10} {'Modified':<20}\n"
                output += "-" * 70 + "\n"
                for item in result:
                    size_str = f"{item['size']} bytes" if item['type'] == 'file' else ""
                    output += f"{item['name']:<30} {item['type']:<10} {size_str:<10} {item['modified']:<20}\n"
                return output
            else:
                return result
        
        elif cmd == 'mkdir':
            if len(parts) > 1:
                return self.create_directory(parts[1])
            else:
                return "Error: Please specify directory name"
        
        elif cmd == 'rm' or cmd == 'rmdir' or cmd == 'del':
            if len(parts) > 1:
                return self.remove_item(parts[1])
            else:
                return "Error: Please specify file or directory name"
        
        elif cmd == 'monitor' or cmd == 'system':
            return self.get_system_monitoring()
        
        elif cmd == 'help':
            return """
Available Commands:
- pwd: Show current directory
- cd <directory>: Change directory
- ls/dir [directory]: List directory contents
- mkdir <name>: Create directory
- rm/del <name>: Remove file or directory
- monitor/system: Show system monitoring info
- help: Show this help message
- clear: Clear terminal
- history: Show command history

Natural Language Commands (examples):
- "create folder mydir"
- "list files"
- "go to documents"
- "show system info"
            """
        
        elif cmd == 'clear':
            return "CLEAR_TERMINAL"
        
        elif cmd == 'history':
            if not self.command_history:
                return "No command history"
            
            output = "Command History:\n\n"
            for i, hist in enumerate(self.command_history[-10:], 1):
                output += f"{i:2d}. {hist['timestamp']} - {hist['command']}\n"
            return output
        
        else:
            # Try to execute as system command
            return self.execute_system_command(command)

# Create terminal instance
terminal = CommandTerminal()

@app.route('/')
def index():
    """Main terminal interface"""
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    """Execute command endpoint"""
    data = request.get_json()
    command = data.get('command', '')
    
    result = terminal.execute_command(command)
    
    return jsonify({
        'output': result,
        'current_dir': terminal.current_dir,
        'system_info': terminal.system_info
    })

@app.route('/monitor')
def get_monitoring():
    """Get system monitoring data"""
    monitoring_data = terminal.get_system_monitoring()
    return jsonify(monitoring_data)

@app.route('/autocomplete')
def autocomplete():
    """Basic autocomplete functionality"""
    query = request.args.get('q', '')
    suggestions = []
    
    # Basic command suggestions
    commands = ['pwd', 'cd', 'ls', 'dir', 'mkdir', 'rm', 'del', 'help', 'clear', 'history', 'monitor', 'system']
    
    for cmd in commands:
        if cmd.startswith(query.lower()):
            suggestions.append(cmd)
    
    # File/directory suggestions for current directory
    if query:
        try:
            for item in os.listdir(terminal.current_dir):
                if item.lower().startswith(query.lower()):
                    suggestions.append(item)
        except:
            pass
    
    return jsonify(suggestions[:10])

if __name__ == '__main__':
    print("Starting Python Command Terminal...")
    print(f"System: {terminal.system_info['platform']} {terminal.system_info['platform_version']}")
    print(f"Python: {terminal.system_info['python_version']}")
    print("Access the terminal at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
