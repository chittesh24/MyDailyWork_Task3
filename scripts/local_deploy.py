"""
Simple local deployment script for testing.
Uses demo mode without requiring trained models.
"""

import os
import sys
import subprocess
import time

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"▶ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ❌ Error: {result.stderr}")
            return False
        print(f"  ✓ {description} completed")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print_header("🚀 LOCAL DEPLOYMENT - IMAGE CAPTIONING SYSTEM")
    
    # Step 1: Generate demo model
    print_header("Step 1: Creating Demo Model")
    if not os.path.exists("backend/checkpoints/demo_model.pth"):
        print("Creating demo model and vocabulary...")
        if run_command("python scripts/create_demo_model.py", "Generate demo model"):
            print("✅ Demo model created")
        else:
            print("❌ Failed to create demo model")
            return
    else:
        print("✅ Demo model already exists")
    
    # Step 2: Setup environment
    print_header("Step 2: Environment Setup")
    if not os.path.exists("backend/.env"):
        print("Creating .env file...")
        with open("backend/.env", "w") as f:
            f.write("""# Local Development Environment
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/image_captions
SECRET_KEY=local-dev-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MODEL_CHECKPOINT_PATH=checkpoints/demo_model.pth
VOCAB_PATH=checkpoints/vocab.json
DEVICE=cpu
MAX_FILE_SIZE_MB=5
ALLOWED_MIME_TYPES=image/jpeg,image/png
RATE_LIMIT_PER_MINUTE=10
ALLOWED_ORIGINS=http://localhost:3000
USE_DEMO_MODE=true
""")
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    # Step 3: Check Docker
    print_header("Step 3: Checking Docker")
    if run_command("docker --version", "Check Docker installation"):
        print("✅ Docker is installed")
    else:
        print("❌ Docker is not installed. Please install Docker Desktop.")
        print("   Download: https://www.docker.com/products/docker-desktop")
        return
    
    if run_command("docker-compose --version", "Check Docker Compose"):
        print("✅ Docker Compose is available")
    else:
        print("❌ Docker Compose not found")
        return
    
    # Step 4: Start services
    print_header("Step 4: Starting Services")
    print("This may take a few minutes on first run...")
    print("\n⏳ Building and starting containers...")
    
    if run_command("docker-compose up -d --build", "Start Docker containers"):
        print("✅ Services started")
    else:
        print("❌ Failed to start services")
        print("\nTrying to stop existing containers first...")
        run_command("docker-compose down", "Stop existing containers")
        if run_command("docker-compose up -d --build", "Restart containers"):
            print("✅ Services started successfully")
        else:
            print("❌ Still failing. Check Docker logs with: docker-compose logs")
            return
    
    # Step 5: Wait for services
    print_header("Step 5: Waiting for Services")
    print("⏳ Waiting for services to be ready...")
    time.sleep(10)
    
    # Step 6: Health check
    print_header("Step 6: Health Check")
    print("Checking service health...")
    
    services_ok = True
    
    # Check database
    result = subprocess.run(
        "docker-compose exec -T db pg_isready -U postgres",
        shell=True,
        capture_output=True
    )
    if result.returncode == 0:
        print("✅ Database: Ready")
    else:
        print("❌ Database: Not ready")
        services_ok = False
    
    # Check backend
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:8000/docs", timeout=5)
        print("✅ Backend API: Ready")
    except:
        print("❌ Backend API: Not ready (may still be starting)")
        services_ok = False
    
    # Check frontend
    try:
        urllib.request.urlopen("http://localhost:3000", timeout=5)
        print("✅ Frontend: Ready")
    except:
        print("❌ Frontend: Not ready (may still be starting)")
        services_ok = False
    
    # Final status
    print_header("🎉 DEPLOYMENT COMPLETE!")
    
    if services_ok:
        print("✅ All services are running!")
    else:
        print("⚠️  Some services are still starting. Wait 1-2 minutes and check again.")
    
    print("""
┌──────────────────────────────────────────────────────────┐
│                    ACCESS YOUR APP                        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  🌐 Frontend:  http://localhost:3000                     │
│  📡 Backend:   http://localhost:8000                     │
│  📚 API Docs:  http://localhost:8000/docs                │
│  🗄️  Database: localhost:5432                            │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                    TEST IMAGES                            │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  📁 Location: test_images/                               │
│     - beach.jpg                                          │
│     - mountain.jpg                                       │
│     - city.jpg                                           │
│     - tree.jpg                                           │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                  USEFUL COMMANDS                          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  View logs:         docker-compose logs -f               │
│  Stop services:     docker-compose down                  │
│  Restart services:  docker-compose restart               │
│  Check status:      docker-compose ps                    │
│                                                           │
└──────────────────────────────────────────────────────────┘

📝 NOTE: This is DEMO MODE with a mock model.
   Expected captions will be generic/placeholder text.
   
   To use a real model:
   1. Train with: bash scripts/train_flickr8k.sh
   2. Or download pre-trained model to backend/checkpoints/
   
🎯 NEXT STEPS:
   1. Open http://localhost:3000 in your browser
   2. Upload test_images/beach.jpg
   3. See the caption generated!
   
""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
