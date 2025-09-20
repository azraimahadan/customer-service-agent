#!/usr/bin/env python3
"""
Setup script for Customer Service Agent project
Creates virtual environment and installs dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and handle errors"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=cwd, 
                              capture_output=True, text=True)
        print(f"✓ {cmd}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ {cmd}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def main():
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"
    
    print("🚀 Setting up Customer Service Agent project...")
    
    # Create virtual environment
    if not venv_path.exists():
        print("\n📦 Creating virtual environment...")
        run_command(f"python -m venv {venv_path}", cwd=project_root)
    else:
        print("\n📦 Virtual environment already exists")
    
    # Activate and install dependencies
    print("\n📥 Installing Python dependencies...")
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    run_command(f'"{pip_path}" install --upgrade pip', cwd=project_root)
    run_command(f'"{pip_path}" install -r requirements.txt', cwd=project_root)
    
    # Install Node.js dependencies for web client
    print("\n🌐 Installing Node.js dependencies...")
    web_client_path = project_root / "web_client"
    if (web_client_path / "package.json").exists():
        run_command("npm install", cwd=web_client_path)
    
    print("\n✅ Setup complete!")
    print(f"\nTo activate the virtual environment:")
    if os.name == 'nt':
        print(f"  {venv_path}\\Scripts\\activate")
    else:
        print(f"  source {venv_path}/bin/activate")
    
    print(f"\nTo deploy the project:")
    print(f"  ./deploy.sh  (or deploy.bat on Windows)")

if __name__ == "__main__":
    main()