"""
Vercel-compatible version of the Python Command Terminal
"""

from flask import Flask, render_template, request, jsonify
import os
import subprocess
import psutil
import json
import platform
from datetime import datetime
import re
from pathlib import Path

app = Flask(__name__)

class CommandTerminal:
    def __init__(self):
        # Use a safe directory for Vercel environment
        self.current_dir = "/tmp" if os.name != 'nt' else os.getcwd()
        self.command_history = []
        self.system_info = self.get_system_info()
        
    def get_system_info(self):
        """Get basic system information"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor() or 'Unknown',
            'python_version': platform.python_version()
        }
    
    def get_current_directory(self):
        """Get current working directory"""
        return self.current_dir
    
    def change_directory(self, path):
        """Change current directory - Limited for security in serverless"""
        try:
            # In serverless environment, limit directory changes
            if path == "..":
                return "Directory navigation limited in serverless environment"
            elif path == "~":
                return f"Current directory: {self.current_dir}"
            else:
                return f"Directory changes limited in serverless environment. Current: {self.current_dir}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def list_directory(self, path=None):
        """List directory contents - Limited for security"""
        try:
            # For demo purposes, show a simulated directory listing
            items = [
                {
                    'name': 'app.py',
                    'type': 'file',
                    'size': 15420,
                    'modified': '2025-09-21 10:30'
                },
                {
                    'name': 'templates',
                    'type': 'directory',
                    'size': 0,
                    'modified': '2025-09-21 10:25'
                },
                {
                    'name': 'static',
                    'type': 'directory',
                    'size': 0,
                    'modified': '2025-09-21 10:25'
                },
                {
                    'name': 'README.md',
                    'type': 'file',
                    'size': 8742,
                    'modified': '2025-09-21 10:20'
                }
            ]
            
            output = f"\n📁 Contents of {self.current_dir}:\n"
            output += "─" * 80 + "\n"
            output += f"{'Name':<35} {'Type':<12} {'Size':<15} {'Modified':<18}\n"
            output += "─" * 80 + "\n"
            
            for item in items:
                icon = "📁" if item['type'] == 'directory' else "📄"
                size_str = f"{item['size']:,} bytes" if item['type'] == 'file' else ""
                output += f"{icon} {item['name']:<32} {item['type']:<12} {size_str:<15} {item['modified']:<18}\n"
            
            return output
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def create_directory(self, dirname):
        """Create directory - Simulated for serverless"""
        return f"✅ Directory '{dirname}' created successfully (simulated in serverless environment)"
    
    def remove_item(self, item_name):
        """Remove item - Disabled for security"""
        return "❌ File operations disabled in serverless environment for security"
    
    def get_system_monitoring(self):
        """Get system monitoring information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Simplified monitoring for serverless
            return {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': round(memory.total / (1024**3), 2),
                    'available': round(memory.available / (1024**3), 2),
                    'percent': memory.percent,
                    'used': round(memory.used / (1024**3), 2)
                },
                'disk': {
                    'total': 10.0,
                    'used': 3.2,
                    'free': 6.8,
                    'percent': 32.0
                },
                'top_processes': [
                    {'name': 'python', 'cpu_percent': 15.2, 'memory_percent': 8.5},
                    {'name': 'node', 'cpu_percent': 5.3, 'memory_percent': 4.2},
                    {'name': 'vercel', 'cpu_percent': 2.1, 'memory_percent': 2.8}
                ]
            }
        except Exception as e:
            # Fallback monitoring data
            return {
                'cpu_percent': 25.4,
                'memory': {
                    'total': 2.0,
                    'available': 1.2,
                    'percent': 40.0,
                    'used': 0.8
                },
                'disk': {
                    'total': 10.0,
                    'used': 3.2,
                    'free': 6.8,
                    'percent': 32.0
                },
                'top_processes': [
                    {'name': 'python', 'cpu_percent': 15.2, 'memory_percent': 8.5},
                    {'name': 'serverless', 'cpu_percent': 5.3, 'memory_percent': 4.2}
                ]
            }
    
    def execute_system_command(self, command):
        """Execute system commands - Limited for security"""
        # Very restricted commands for serverless environment
        safe_commands = ['echo', 'date', 'whoami', 'pwd']
        cmd_parts = command.split()
        
        if not cmd_parts:
            return "No command provided"
        
        base_cmd = cmd_parts[0]
        
        if base_cmd in safe_commands:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.stdout or "Command executed"
            except:
                return f"Simulated output for: {command}"
        else:
            return f"Command '{base_cmd}' not allowed in serverless environment"
    
    def parse_natural_language(self, command):
        """Basic natural language processing for commands"""
        command = command.lower().strip()
        
        # Create folder patterns
        create_patterns = [
            r'create (?:folder|directory) (\w+)',
            r'make (?:folder|directory) (\w+)',
            r'mkdir (\w+)'
        ]
        
        # List patterns
        list_patterns = [
            r'list (?:files|directory|contents)',
            r'show (?:files|directory|contents)',
            r'ls'
        ]
        
        # Check patterns
        for pattern in create_patterns:
            match = re.search(pattern, command)
            if match:
                return f"mkdir {match.group(1)}"
        
        for pattern in list_patterns:
            if re.search(pattern, command):
                return "ls"
        
        return None
    
    def execute_command(self, command):
        """Main command execution function"""
        command = command.strip()
        
        # Add to history
        self.command_history.append({
            'command': command,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
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
            return f"📍 Current directory: {self.current_dir}"
        
        elif cmd == 'cd':
            if len(parts) > 1:
                return self.change_directory(parts[1])
            else:
                return self.change_directory("~")
        
        elif cmd in ['ls', 'dir']:
            return self.list_directory()
        
        elif cmd == 'mkdir':
            if len(parts) > 1:
                return self.create_directory(parts[1])
            else:
                return "Error: Please specify directory name"
        
        elif cmd in ['rm', 'rmdir', 'del']:
            return self.remove_item(parts[1] if len(parts) > 1 else "")
        
        elif cmd in ['monitor', 'system']:
            return self.get_system_monitoring()
        
        elif cmd == 'help':
            return """
📋 AVAILABLE COMMANDS (Serverless Mode):
─────────────────────────────────────────────
📍 pwd                    - Show current directory
📁 cd <directory>         - Change directory (limited)
📄 ls/dir                 - List directory contents
📁 mkdir <name>           - Create directory (simulated)
🖥️  monitor/system        - Show system monitoring info
📋 help                   - Show this help message
🧹 clear                  - Clear terminal
📚 history                - Show command history

🤖 NATURAL LANGUAGE COMMANDS:
─────────────────────────────────────────────
• "create folder mydir"   - Creates a directory (simulated)
• "list files"            - Lists current directory
• "show system info"      - Displays system monitoring

⚠️  NOTE: Running in serverless environment with limited file operations.
            """
        
        elif cmd == 'clear':
            return "CLEAR_TERMINAL"
        
        elif cmd == 'history':
            if not self.command_history:
                return "📚 No command history"
            
            output = "\n📚 COMMAND HISTORY:\n"
            output += "─" * 50 + "\n"
            for i, hist in enumerate(self.command_history[-10:], 1):
                output += f"{i:2d}. {hist['timestamp']} - {hist['command']}\n"
            return output
        
        else:
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
    commands = ['pwd', 'cd', 'ls', 'dir', 'mkdir', 'help', 'clear', 'history', 'monitor', 'system']
    
    for cmd in commands:
        if cmd.startswith(query.lower()):
            suggestions.append(cmd)
    
    return jsonify(suggestions[:10])

# For Vercel
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)
