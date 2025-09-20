#!/usr/bin/env python3
"""
Python Command Terminal Launcher
Allows users to choose between CLI and Web interface
"""

import sys
import os
import subprocess
import argparse

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import psutil
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies.")
        return False

def launch_web_terminal():
    """Launch the web-based terminal"""
    print("🚀 Starting Web Terminal...")
    print("📱 Access at: http://localhost:5000")
    print("🔥 Press Ctrl+C to stop the server")
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Web terminal stopped.")

def launch_cli_terminal():
    """Launch the CLI terminal"""
    print("🚀 Starting CLI Terminal...")
    try:
        subprocess.run([sys.executable, "cli_terminal.py"])
    except KeyboardInterrupt:
        print("\n👋 CLI terminal stopped.")

def main():
    parser = argparse.ArgumentParser(description="Python Command Terminal Launcher")
    parser.add_argument("--mode", choices=["cli", "web", "auto"], default="auto",
                      help="Launch mode: cli, web, or auto (interactive)")
    parser.add_argument("--install-deps", action="store_true",
                      help="Install dependencies and exit")
    
    args = parser.parse_args()
    
    # Handle dependency installation
    if args.install_deps:
        if install_dependencies():
            print("✅ Dependencies installed. You can now run the terminal.")
        else:
            print("❌ Failed to install dependencies.")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Required dependencies not found.")
        print("📦 Run with --install-deps to install them:")
        print(f"   python {sys.argv[0]} --install-deps")
        return
    
    # Display welcome message
    print("=" * 60)
    print("🐍 PYTHON COMMAND TERMINAL LAUNCHER")
    print("=" * 60)
    print("Choose your preferred interface:")
    print()
    
    if args.mode == "auto":
        print("1. 🖥️  CLI Terminal (Command Line Interface)")
        print("2. 🌐 Web Terminal (Browser Interface)")
        print("3. ❌ Exit")
        print()
        
        while True:
            try:
                choice = input("Enter your choice (1-3): ").strip()
                
                if choice == "1":
                    launch_cli_terminal()
                    break
                elif choice == "2":
                    launch_web_terminal()
                    break
                elif choice == "3":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1, 2, or 3.")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
    
    elif args.mode == "cli":
        launch_cli_terminal()
    
    elif args.mode == "web":
        launch_web_terminal()

if __name__ == "__main__":
    main()
