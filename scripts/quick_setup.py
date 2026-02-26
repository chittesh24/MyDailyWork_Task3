#!/usr/bin/env python3
"""
Quick setup script for local development.
Sets up environment with sensible defaults.
"""

import os
import sys
import secrets
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def setup_backend_env():
    """Setup backend .env file."""
    print_header("Setting up Backend Environment")
    
    backend_dir = Path(__file__).parent.parent / "backend"
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    if env_file.exists():
        print("✅ .env file already exists")
        overwrite = input("Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Keeping existing .env file")
            return
    
    print("Creating .env file from template...")
    
    # Read template
    with open(env_example) as f:
        content = f.read()
    
    # Generate secret key
    secret_key = secrets.token_hex(32)
    
    # Replace placeholders
    content = content.replace(
        'your-secret-key-here-minimum-32-characters',
        secret_key
    )
    
    # Use local database URL for development
    content = content.replace(
        'DATABASE_URL=postgresql://user:password@localhost:5432/image_captions',
        'DATABASE_URL=postgresql://postgres:postgres@db:5432/image_captions'
    )
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Created {env_file}")
    print(f"✅ Generated secret key: {secret_key[:20]}...")

def setup_frontend_env():
    """Setup frontend .env.local file."""
    print_header("Setting up Frontend Environment")
    
    frontend_dir = Path(__file__).parent.parent / "frontend"
    env_file = frontend_dir / ".env.local"
    
    if env_file.exists():
        print("✅ .env.local file already exists")
        return
    
    print("Creating .env.local file...")
    
    content = "NEXT_PUBLIC_API_URL=http://localhost:8000\n"
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Created {env_file}")

def fix_permissions():
    """Fix script permissions."""
    print_header("Fixing Script Permissions")
    
    scripts_dir = Path(__file__).parent
    
    # Make all .sh scripts executable
    sh_scripts = list(scripts_dir.glob("*.sh"))
    for script in sh_scripts:
        os.chmod(script, 0o755)
        print(f"✅ Made executable: {script.name}")
    
    # Make Python scripts executable
    py_scripts = list(scripts_dir.glob("*.py"))
    for script in py_scripts:
        os.chmod(script, 0o755)
        print(f"✅ Made executable: {script.name}")

def check_docker():
    """Check if Docker is installed and running."""
    print_header("Checking Docker")
    
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found")
        print("   Install from: https://www.docker.com/get-started")
        return False
    
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker Compose not found")
        return False
    
    # Check if Docker daemon is running
    try:
        subprocess.run(['docker', 'ps'], 
                      capture_output=True, check=True)
        print("✅ Docker daemon is running")
        return True
    except subprocess.CalledProcessError:
        print("❌ Docker daemon not running")
        print("   Start Docker Desktop or run: sudo systemctl start docker")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Dependencies")
    
    backend_dir = Path(__file__).parent.parent / "backend"
    req_file = backend_dir / "requirements.txt"
    
    install = input("Install Python dependencies? (y/N): ").strip().lower()
    if install == 'y':
        print("Installing dependencies...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(req_file)],
                         check=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    else:
        print("Skipped dependency installation")
    
    return True

def print_next_steps():
    """Print next steps."""
    print_header("Setup Complete! 🎉")
    
    print("\n📋 Next Steps:\n")
    print("1. Start the application:")
    print("   docker-compose up -d")
    print()
    print("2. Or use one-click deployment:")
    print("   bash scripts/one_click_deploy.sh")
    print()
    print("3. Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend:  http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print()
    print("4. Train a model (optional):")
    print("   bash scripts/train_flickr8k.sh")
    print()
    print("5. For production deployment:")
    print("   python scripts/setup_free_tier.py")
    print()

def main():
    """Main setup function."""
    print("="*60)
    print("  🚀 Quick Setup - Image Captioning System")
    print("="*60)
    
    # Setup environments
    setup_backend_env()
    setup_frontend_env()
    
    # Fix permissions
    fix_permissions()
    
    # Check Docker
    docker_ok = check_docker()
    
    # Install dependencies (optional)
    install_dependencies()
    
    # Print next steps
    print_next_steps()
    
    if not docker_ok:
        print("\n⚠️  Docker is not ready. Please install/start Docker first.")
        return 1
    
    print("\n✨ Setup complete! You're ready to go!\n")
    return 0

if __name__ == '__main__':
    sys.exit(main())
