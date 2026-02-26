#!/usr/bin/env python3
"""
Run local backend server without Docker.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add backend to path
project_root = Path(__file__).parent.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    print("\n" + "="*60)
    print("  🚀 STARTING BACKEND SERVER (NO DOCKER)")
    print("="*60 + "\n")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Copy .env.local to .env if .env doesn't exist
    env_local = backend_dir / ".env.local"
    env_file = backend_dir / ".env"
    
    if not env_file.exists() and env_local.exists():
        print("📋 Copying .env.local to .env...")
        import shutil
        shutil.copy(env_local, env_file)
        print("✅ Environment file created\n")
    
    # Initialize database
    print("📊 Initializing database...")
    try:
        from database.init_sqlite import init_sqlite_db
        init_sqlite_db()
        print("✅ Database ready\n")
    except Exception as e:
        print(f"⚠️  Database initialization: {e}")
        print("   Continuing anyway...\n")
    
    # Create checkpoints directory
    checkpoints_dir = backend_dir / "checkpoints"
    checkpoints_dir.mkdir(exist_ok=True)
    
    # Create demo model if it doesn't exist
    demo_model = checkpoints_dir / "demo_model.pth"
    demo_vocab = checkpoints_dir / "demo_vocab.json"
    
    if not demo_model.exists() or not demo_vocab.exists():
        print("🤖 Creating demo model...")
        try:
            sys.path.insert(0, str(project_root / "scripts"))
            from create_demo_model import create_demo_model
            create_demo_model()
            print("✅ Demo model created\n")
        except Exception as e:
            print(f"⚠️  Could not create demo model: {e}")
            print("   API will use demo predictor instead\n")
    
    print("="*60)
    print("  ✅ BACKEND STARTING...")
    print("="*60)
    print(f"\n  🌐 API URL: http://localhost:8000")
    print(f"  📚 API Docs: http://localhost:8000/docs")
    print(f"  🔍 Health Check: http://localhost:8000/health")
    print("\n  Press Ctrl+C to stop\n")
    print("="*60 + "\n")
    
    # Start uvicorn server
    try:
        import uvicorn
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n✅ Backend server stopped.")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you installed dependencies: pip install -r requirements.txt")
        print("2. Check if port 8000 is already in use")
        print("3. See NO_DOCKER_SETUP.md for help")
        sys.exit(1)

if __name__ == "__main__":
    main()
