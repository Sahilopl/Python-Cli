"""
CLI Version of Python Command Terminal
A command-line interface version for users who prefer terminal-only interaction
"""

import os
import subprocess
import psutil
import platform
import shlex
from datetime import datetime
import atexit
import json

# Try to import readline, fallback for Windows
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False
    print("Note: readline not available on this system. History and autocomplete disabled.")

class CLITerminal:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.command_history = []
        self.setup_readline()
        self.system_info = self.get_system_info()
        
        # Display welcome message
        self.display_welcome()
    
    def setup_readline(self):
        """Setup command history and autocomplete"""
        if not READLINE_AVAILABLE:
            return
            
        histfile = os.path.join(os.path.expanduser("~"), ".python_terminal_history")
        try:
            readline.read_history_file(histfile)
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass
        
        atexit.register(readline.write_history_file, histfile)
        
        # Setup tab completion
        readline.set_completer(self.completer)
        readline.parse_and_bind('tab: complete')
    
    def completer(self, text, state):
        """Auto-completion function"""
        if not READLINE_AVAILABLE:
            return None
            
        commands = ['pwd', 'cd', 'ls', 'dir', 'mkdir', 'rm', 'rmdir', 'del', 'help', 'clear', 'history', 'monitor', 'system', 'exit', 'quit']
        
        # Get files and directories in current directory
        try:
            files_dirs = [f for f in os.listdir(self.current_dir) if f.startswith(text)]
            options = [cmd for cmd in commands if cmd.startswith(text)] + files_dirs
        except:
            options = [cmd for cmd in commands if cmd.startswith(text)]
        
        if state < len(options):
            return options[state]
        else:
            return None
    
    def get_system_info(self):
        """Get basic system information"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def display_welcome(self):
        """Display welcome message"""
        print("=" * 70)
        print("🐍 PYTHON COMMAND TERMINAL - CLI VERSION")
        print("=" * 70)
        print(f"System: {self.system_info['platform']} {self.system_info['platform_version']}")
        print(f"Python: {self.system_info['python_version']}")
        print(f"Architecture: {self.system_info['architecture']}")
        print()
        print("📋 Available Commands:")
        print("  pwd, cd, ls/dir, mkdir, rm/del, monitor, help, clear, history, exit")
        print()
        print("🤖 Natural Language Support:")
        print("  'create folder test', 'list files', 'show system info'")
        print("=" * 70)
        print()
    
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
                return f"✅ Changed directory to: {self.current_dir}"
            else:
                return f"❌ Error: Directory '{path}' not found"
        except Exception as e:
            return f"❌ Error changing directory: {str(e)}"
    
    def list_directory(self, path=None):
        """List directory contents"""
        try:
            target_dir = path if path else self.current_dir
            if not os.path.isabs(target_dir):
                target_dir = os.path.join(self.current_dir, target_dir)
            
            if not os.path.exists(target_dir):
                return f"❌ Error: Directory '{target_dir}' not found"
            
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
            
            # Format output
            if not items:
                return "📁 Directory is empty"
            
            output = f"\n📁 Contents of {target_dir}:\n"
            output += "─" * 80 + "\n"
            output += f"{'Name':<35} {'Type':<12} {'Size':<15} {'Modified':<18}\n"
            output += "─" * 80 + "\n"
            
            for item in sorted(items, key=lambda x: (x['type'], x['name'].lower())):
                icon = "📁" if item['type'] == 'directory' else "📄"
                size_str = f"{item['size']:,} bytes" if item['type'] == 'file' else ""
                output += f"{icon} {item['name']:<32} {item['type']:<12} {size_str:<15} {item['modified']:<18}\n"
            
            return output
        except Exception as e:
            return f"❌ Error listing directory: {str(e)}"
    
    def create_directory(self, dirname):
        """Create a new directory"""
        try:
            if not os.path.isabs(dirname):
                dirname = os.path.join(self.current_dir, dirname)
            
            os.makedirs(dirname, exist_ok=True)
            return f"✅ Directory '{dirname}' created successfully"
        except Exception as e:
            return f"❌ Error creating directory: {str(e)}"
    
    def remove_item(self, item_name):
        """Remove file or directory"""
        try:
            if not os.path.isabs(item_name):
                item_path = os.path.join(self.current_dir, item_name)
            else:
                item_path = item_name
            
            if not os.path.exists(item_path):
                return f"❌ Error: '{item_name}' not found"
            
            if os.path.isdir(item_path):
                os.rmdir(item_path)
                return f"✅ Directory '{item_name}' removed successfully"
            else:
                os.remove(item_path)
                return f"✅ File '{item_name}' removed successfully"
        except Exception as e:
            return f"❌ Error removing '{item_name}': {str(e)}"
    
    def get_system_monitoring(self):
        """Get system monitoring information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/' if os.name != 'nt' else 'C:')
            
            # Get top processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage and get top 5
            processes = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:5]
            
            # Format output
            output = "\n🖥️  SYSTEM MONITORING\n"
            output += "=" * 50 + "\n"
            
            # CPU Info
            output += f"🔥 CPU Usage: {cpu_percent:.1f}%\n"
            output += f"{'█' * int(cpu_percent / 2)}{' ' * (50 - int(cpu_percent / 2))}\n\n"
            
            # Memory Info
            memory_gb = memory.total / (1024**3)
            used_gb = memory.used / (1024**3)
            available_gb = memory.available / (1024**3)
            
            output += f"💾 Memory Usage: {memory.percent:.1f}%\n"
            output += f"   Total: {memory_gb:.1f} GB\n"
            output += f"   Used:  {used_gb:.1f} GB\n"
            output += f"   Free:  {available_gb:.1f} GB\n"
            output += f"{'█' * int(memory.percent / 2)}{' ' * (50 - int(memory.percent / 2))}\n\n"
            
            # Disk Info
            disk_gb = disk.total / (1024**3)
            used_disk_gb = disk.used / (1024**3)
            free_disk_gb = disk.free / (1024**3)
            disk_percent = (disk.used / disk.total) * 100
            
            output += f"💿 Disk Usage: {disk_percent:.1f}%\n"
            output += f"   Total: {disk_gb:.1f} GB\n"
            output += f"   Used:  {used_disk_gb:.1f} GB\n"
            output += f"   Free:  {free_disk_gb:.1f} GB\n"
            output += f"{'█' * int(disk_percent / 2)}{' ' * (50 - int(disk_percent / 2))}\n\n"
            
            # Top Processes
            output += "🚀 Top Processes (by CPU):\n"
            output += "-" * 50 + "\n"
            for i, proc in enumerate(processes, 1):
                name = proc['name'][:25] if proc['name'] else 'Unknown'
                cpu = proc['cpu_percent'] or 0
                mem = proc['memory_percent'] or 0
                output += f"{i}. {name:<25} CPU: {cpu:5.1f}% | MEM: {mem:5.1f}%\n"
            
            return output
        except Exception as e:
            return f"❌ Error getting system information: {str(e)}"
    
    def execute_system_command(self, command):
        """Execute system commands safely"""
        try:
            # Restricted commands for security
            dangerous_commands = ['rm -rf', 'format', 'del /f', 'shutdown', 'reboot']
            if any(danger in command.lower() for danger in dangerous_commands):
                return "❌ Error: Command not allowed for security reasons"
            
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
                output += f"\n❌ Error: {result.stderr}"
            
            return output if output else "✅ Command executed successfully"
        except subprocess.TimeoutExpired:
            return "❌ Error: Command timed out"
        except Exception as e:
            return f"❌ Error executing command: {str(e)}"
    
    def parse_natural_language(self, command):
        """Basic natural language processing for commands"""
        import re
        
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
        
        # Change directory patterns
        cd_patterns = [
            r'(?:go to|change to|cd) (\w+)',
            r'enter (?:directory|folder) (\w+)'
        ]
        
        # System monitoring patterns
        monitor_patterns = [
            r'show system (?:info|information|monitor)',
            r'system (?:monitor|info)',
            r'monitor'
        ]
        
        # Check patterns
        for pattern in create_patterns:
            match = re.search(pattern, command)
            if match:
                return f"mkdir {match.group(1)}"
        
        for pattern in list_patterns:
            if re.search(pattern, command):
                return "ls"
        
        for pattern in cd_patterns:
            match = re.search(pattern, command)
            if match:
                return f"cd {match.group(1)}"
        
        for pattern in monitor_patterns:
            if re.search(pattern, command):
                return "monitor"
        
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
            return "❌ No command entered"
        
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
                return self.change_directory(os.path.expanduser("~"))
        
        elif cmd in ['ls', 'dir']:
            if len(parts) > 1:
                return self.list_directory(parts[1])
            else:
                return self.list_directory()
        
        elif cmd == 'mkdir':
            if len(parts) > 1:
                return self.create_directory(parts[1])
            else:
                return "❌ Error: Please specify directory name"
        
        elif cmd in ['rm', 'rmdir', 'del']:
            if len(parts) > 1:
                return self.remove_item(parts[1])
            else:
                return "❌ Error: Please specify file or directory name"
        
        elif cmd in ['monitor', 'system']:
            return self.get_system_monitoring()
        
        elif cmd == 'help':
            return """
📋 AVAILABLE COMMANDS:
─────────────────────────────────────────────
📍 pwd                    - Show current directory
📁 cd <directory>         - Change directory
📄 ls/dir [directory]     - List directory contents
📁 mkdir <name>           - Create directory
🗑️  rm/del <name>          - Remove file or directory
🖥️  monitor/system        - Show system monitoring info
📋 help                   - Show this help message
🧹 clear                  - Clear terminal
📚 history                - Show command history
🚪 exit/quit              - Exit terminal

🤖 NATURAL LANGUAGE COMMANDS:
─────────────────────────────────────────────
• "create folder mydir"   - Creates a directory
• "list files"            - Lists current directory
• "go to documents"       - Changes to documents folder
• "show system info"      - Displays system monitoring

💡 TIPS:
─────────────────────────────────────────────
• Use Tab for auto-completion
• Use ↑/↓ arrows for command history
• Type 'exit' or 'quit' to close terminal
            """
        
        elif cmd == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            self.display_welcome()
            return ""
        
        elif cmd == 'history':
            if not self.command_history:
                return "📚 No command history"
            
            output = "\n📚 COMMAND HISTORY:\n"
            output += "─" * 50 + "\n"
            for i, hist in enumerate(self.command_history[-10:], 1):
                output += f"{i:2d}. {hist['timestamp']} - {hist['command']}\n"
            return output
        
        elif cmd in ['exit', 'quit']:
            print("\n👋 Thank you for using Python Command Terminal!")
            print("Goodbye! 🐍")
            exit(0)
        
        else:
            # Try to execute as system command
            return self.execute_system_command(command)
    
    def run(self):
        """Main terminal loop"""
        try:
            while True:
                try:
                    # Create prompt
                    short_dir = self.current_dir.replace(os.path.expanduser("~"), "~")
                    if len(short_dir) > 40:
                        short_dir = "..." + short_dir[-37:]
                    
                    prompt = f"\n🐍 {short_dir} $ "
                    
                    # Get user input
                    command = input(prompt).strip()
                    
                    if command:
                        result = self.execute_command(command)
                        if result:
                            print(result)
                
                except KeyboardInterrupt:
                    print("\n\n👋 Exiting Python Command Terminal...")
                    print("Goodbye! 🐍")
                    break
                
                except EOFError:
                    print("\n\n👋 Exiting Python Command Terminal...")
                    print("Goodbye! 🐍")
                    break
        
        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")
            print("Terminal will now exit.")

def main():
    """Main function to start CLI terminal"""
    try:
        terminal = CLITerminal()
        terminal.run()
    except Exception as e:
        print(f"❌ Error starting terminal: {str(e)}")

if __name__ == "__main__":
    main()
