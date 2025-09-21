"""
Vercel-compatible Python Command Terminal
Simplified version without psutil for serverless deployment
"""

from flask import Flask, render_template, request, jsonify
import os
import platform
from datetime import datetime
import re

app = Flask(__name__)

class SimpleTerminal:
    def __init__(self):
        self.current_dir = "/tmp"
        self.command_history = []
        self.system_info = self.get_system_info()
        
    def get_system_info(self):
        """Get basic system information"""
        return {
            'platform': 'Linux',
            'platform_version': 'Serverless',
            'architecture': 'x64',
            'processor': 'Serverless Function',
            'python_version': platform.python_version()
        }
    
    def list_directory(self):
        """Simulated directory listing for demo"""
        items = [
            {'name': 'app.py', 'type': 'file', 'size': 15420, 'modified': '2025-09-21 10:30'},
            {'name': 'templates', 'type': 'directory', 'size': 0, 'modified': '2025-09-21 10:25'},
            {'name': 'static', 'type': 'directory', 'size': 0, 'modified': '2025-09-21 10:25'},
            {'name': 'README.md', 'type': 'file', 'size': 8742, 'modified': '2025-09-21 10:20'},
            {'name': 'requirements.txt', 'type': 'file', 'size': 256, 'modified': '2025-09-21 10:15'}
        ]
        
        output = f"\n📁 Contents of {self.current_dir} (Serverless Demo):\n"
        output += "─" * 80 + "\n"
        output += f"{'Name':<35} {'Type':<12} {'Size':<15} {'Modified':<18}\n"
        output += "─" * 80 + "\n"
        
        for item in items:
            icon = "📁" if item['type'] == 'directory' else "📄"
            size_str = f"{item['size']:,} bytes" if item['type'] == 'file' else ""
            output += f"{icon} {item['name']:<32} {item['type']:<12} {size_str:<15} {item['modified']:<18}\n"
        
        return output
    
    def get_system_monitoring(self):
        """Simulated system monitoring for serverless"""
        return {
            'cpu_percent': 15.2,
            'memory': {
                'total': 1.0,
                'available': 0.7,
                'percent': 30.0,
                'used': 0.3
            },
            'disk': {
                'total': 10.0,
                'used': 2.1,
                'free': 7.9,
                'percent': 21.0
            },
            'top_processes': [
                {'name': 'python3', 'cpu_percent': 12.4, 'memory_percent': 15.2},
                {'name': 'vercel-runtime', 'cpu_percent': 2.8, 'memory_percent': 8.1},
                {'name': 'node', 'cpu_percent': 1.5, 'memory_percent': 4.3}
            ]
        }
    
    def parse_natural_language(self, command):
        """Basic natural language processing"""
        command = command.lower().strip()
        
        if re.search(r'create (?:folder|directory) (\w+)', command):
            match = re.search(r'create (?:folder|directory) (\w+)', command)
            return f"mkdir {match.group(1)}"
        elif re.search(r'list (?:files|directory|contents)', command):
            return "ls"
        elif re.search(r'show system (?:info|monitor)', command):
            return "monitor"
        
        return None
    
    def execute_command(self, command):
        """Execute commands with serverless limitations"""
        original_command = command
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
        
        # Try natural language processing
        parsed = self.parse_natural_language(command)
        if parsed:
            command = parsed
        
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == 'pwd':
            return f"📍 Current directory: {self.current_dir} (Serverless Environment)"
        
        elif cmd in ['ls', 'dir']:
            return self.list_directory()
        
        elif cmd == 'mkdir':
            dirname = parts[1] if len(parts) > 1 else "newdir"
            return f"✅ Directory '{dirname}' created successfully (simulated in serverless)"
        
        elif cmd in ['rm', 'del']:
            filename = parts[1] if len(parts) > 1 else "file"
            return f"✅ '{filename}' removed successfully (simulated in serverless)"
        
        elif cmd in ['monitor', 'system']:
            return self.get_system_monitoring()
        
        elif cmd == 'help':
            return """
📋 SERVERLESS TERMINAL COMMANDS:
─────────────────────────────────────────────
📍 pwd                    - Show current directory
📄 ls/dir                 - List directory contents (demo)
📁 mkdir <name>           - Create directory (simulated)
🗑️  rm/del <name>          - Remove item (simulated)
🖥️  monitor/system        - Show system info
📋 help                   - Show this help
🧹 clear                  - Clear terminal
📚 history                - Show command history

🤖 NATURAL LANGUAGE:
─────────────────────────────────────────────
• "create folder test"    - mkdir test
• "list files"            - ls
• "show system info"      - monitor

⚠️  Running in Vercel serverless environment
   Some features are simulated for security.
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
        
        elif cmd == 'cd':
            target = parts[1] if len(parts) > 1 else "~"
            return f"📍 Directory navigation limited in serverless. Current: {self.current_dir}"
        
        elif cmd in ['echo']:
            text = ' '.join(parts[1:]) if len(parts) > 1 else ""
            return f"🔊 {text}"
        
        elif cmd == 'date':
            return f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        elif cmd == 'whoami':
            return "👤 vercel-user (serverless)"
        
        else:
            return f"Command '{cmd}' not available in serverless environment. Type 'help' for available commands."

# Create terminal instance
terminal = SimpleTerminal()

@app.route('/')
def index():
    """Main terminal interface"""
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    """Execute command endpoint"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        result = terminal.execute_command(command)
        
        return jsonify({
            'output': result,
            'current_dir': terminal.current_dir,
            'system_info': terminal.system_info
        })
    except Exception as e:
        return jsonify({
            'output': f"Error: {str(e)}",
            'current_dir': terminal.current_dir,
            'system_info': terminal.system_info
        }), 500

@app.route('/monitor')
def get_monitoring():
    """Get system monitoring data"""
    try:
        monitoring_data = terminal.get_system_monitoring()
        return jsonify(monitoring_data)
    except Exception as e:
        return jsonify({
            'error': f"Monitoring error: {str(e)}",
            'cpu_percent': 0,
            'memory': {'percent': 0},
            'disk': {'percent': 0},
            'top_processes': []
        }), 500

@app.route('/autocomplete')
def autocomplete():
    """Basic autocomplete functionality"""
    try:
        query = request.args.get('q', '')
        commands = ['pwd', 'cd', 'ls', 'dir', 'mkdir', 'rm', 'del', 'help', 'clear', 'history', 'monitor', 'echo', 'date', 'whoami']
        
        suggestions = [cmd for cmd in commands if cmd.startswith(query.lower())]
        return jsonify(suggestions[:10])
    except Exception as e:
        return jsonify([])

# Vercel handler
app.wsgi_app = app.wsgi_app

if __name__ == '__main__':
    app.run(debug=True)
