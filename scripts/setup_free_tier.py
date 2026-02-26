"""
Complete setup script for free tier deployment.
Automates deployment to Render + Vercel + Supabase.
"""

import os
import sys
import subprocess
from pathlib import Path
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def check_prerequisites():
    """Check if required tools are installed."""
    console.print("\n[bold cyan]Checking prerequisites...[/bold cyan]")
    
    required = {
        'git': 'git --version',
        'npm': 'npm --version',
        'python': 'python --version'
    }
    
    optional = {
        'vercel': 'vercel --version',
        'render': 'render --version'
    }
    
    missing = []
    
    for tool, cmd in required.items():
        try:
            subprocess.run(cmd.split(), capture_output=True, check=True)
            console.print(f"✅ {tool} found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print(f"❌ {tool} not found")
            missing.append(tool)
    
    if missing:
        console.print(f"\n[bold red]Missing required tools: {', '.join(missing)}[/bold red]")
        return False
    
    # Check optional
    for tool, cmd in optional.items():
        try:
            subprocess.run(cmd.split(), capture_output=True, check=True)
            console.print(f"✅ {tool} CLI found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print(f"⚠️  {tool} CLI not found (will use manual deployment)")
    
    return True


def setup_supabase():
    """Guide user through Supabase setup."""
    console.print("\n[bold cyan]Setting up Supabase Database[/bold cyan]")
    
    console.print(Panel.fit(
        "[bold]Supabase Setup Instructions[/bold]\n\n"
        "1. Visit https://supabase.com and sign up\n"
        "2. Create new project: 'image-captioning'\n"
        "3. Choose free tier (500MB)\n"
        "4. Copy your database password\n"
        "5. Go to Settings > Database\n"
        "6. Copy connection string\n"
        "7. Run the SQL schema (backend/database/schema.sql)",
        title="📊 Database Setup"
    ))
    
    connection_string = questionary.text(
        "Paste your Supabase connection string:",
        validate=lambda x: "postgresql://" in x
    ).ask()
    
    return connection_string


def deploy_backend_render():
    """Guide through Render deployment."""
    console.print("\n[bold cyan]Deploying Backend to Render[/bold cyan]")
    
    console.print(Panel.fit(
        "[bold]Render Deployment Instructions[/bold]\n\n"
        "1. Visit https://dashboard.render.com\n"
        "2. Create New > Web Service\n"
        "3. Connect your GitHub repository\n"
        "4. Configure:\n"
        "   - Root Directory: backend\n"
        "   - Build Command: pip install -r requirements.txt\n"
        "   - Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT\n"
        "5. Add environment variables (see below)\n"
        "6. Click 'Create Web Service'",
        title="🚀 Backend Deployment"
    ))
    
    console.print("\n[bold]Required Environment Variables:[/bold]")
    console.print("DATABASE_URL: <your-supabase-connection-string>")
    console.print("SECRET_KEY: <generate-random-string>")
    console.print("DEVICE: cpu")
    console.print("ALLOWED_ORIGINS: https://your-app.vercel.app")
    
    input("\nPress Enter once deployment is complete...")
    
    backend_url = questionary.text(
        "Enter your Render backend URL (e.g., https://your-app.onrender.com):"
    ).ask()
    
    return backend_url


def deploy_frontend_vercel(backend_url):
    """Deploy frontend to Vercel."""
    console.print("\n[bold cyan]Deploying Frontend to Vercel[/bold cyan]")
    
    # Check if vercel CLI is available
    try:
        subprocess.run(['vercel', '--version'], capture_output=True, check=True)
        use_cli = questionary.confirm("Use Vercel CLI for deployment?").ask()
    except (subprocess.CalledProcessError, FileNotFoundError):
        use_cli = False
    
    if use_cli:
        console.print("\nDeploying with Vercel CLI...")
        os.chdir('frontend')
        
        # Login
        subprocess.run(['vercel', 'login'])
        
        # Set environment variable
        subprocess.run([
            'vercel', 'env', 'add', 'NEXT_PUBLIC_API_URL',
            'production'
        ], input=backend_url.encode())
        
        # Deploy
        result = subprocess.run(['vercel', '--prod'], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("\n✅ Frontend deployed successfully!")
            # Extract URL from output
            for line in result.stdout.split('\n'):
                if 'https://' in line:
                    frontend_url = line.strip()
                    break
        else:
            console.print(f"\n❌ Deployment failed: {result.stderr}")
            return None
    else:
        console.print(Panel.fit(
            "[bold]Manual Vercel Deployment[/bold]\n\n"
            "1. Visit https://vercel.com\n"
            "2. Import your GitHub repository\n"
            "3. Set Root Directory to: frontend\n"
            "4. Add environment variable:\n"
            f"   NEXT_PUBLIC_API_URL={backend_url}\n"
            "5. Click 'Deploy'",
            title="🎨 Frontend Deployment"
        ))
        
        frontend_url = questionary.text(
            "Enter your Vercel frontend URL (e.g., https://your-app.vercel.app):"
        ).ask()
    
    return frontend_url


def update_cors(backend_url, frontend_url):
    """Update CORS settings."""
    console.print("\n[bold cyan]Updating CORS Settings[/bold cyan]")
    
    console.print(f"\nUpdate ALLOWED_ORIGINS in Render:")
    console.print(f"  ALLOWED_ORIGINS={frontend_url}")
    
    input("\nPress Enter once updated...")


def create_summary(db_url, backend_url, frontend_url):
    """Create deployment summary."""
    summary = f"""
╔══════════════════════════════════════════════════════════╗
║           DEPLOYMENT SUMMARY                              ║
╚══════════════════════════════════════════════════════════╝

🗄️  Database (Supabase):
   {db_url[:50]}...

🚀 Backend (Render):
   {backend_url}

🎨 Frontend (Vercel):
   {frontend_url}

📝 NEXT STEPS:

1. Update CORS in Render:
   Go to Render Dashboard → Environment
   Set ALLOWED_ORIGINS={frontend_url}

2. Upload Model Files:
   - Upload best_model.pth to Render
   - Upload vocab.json to Render
   - Or use external storage (S3, Google Drive)

3. Test Your Deployment:
   Visit: {frontend_url}
   Register an account
   Generate a caption!

💰 COST BREAKDOWN:
   - Supabase: $0/month (500MB free)
   - Render: $0/month (750 hours free)
   - Vercel: $0/month (unlimited free)
   
   Total: $0/month 🎉

⚠️  FREE TIER LIMITATIONS:
   - Render: Cold starts after 15min inactivity
   - Supabase: 500MB database limit
   - Model inference on CPU (slower)

🔗 USEFUL LINKS:
   - Render Dashboard: https://dashboard.render.com
   - Vercel Dashboard: https://vercel.com/dashboard
   - Supabase Dashboard: https://app.supabase.com

"""
    
    # Save to file
    with open('DEPLOYMENT_INFO.txt', 'w') as f:
        f.write(summary)
    
    console.print(Panel.fit(summary, title="🎉 Deployment Complete!"))
    console.print("\n✅ Summary saved to DEPLOYMENT_INFO.txt")


def main():
    """Main deployment orchestrator."""
    console.print(Panel.fit(
        "[bold cyan]Free Tier Deployment Setup[/bold cyan]\n\n"
        "This script will guide you through deploying to:\n"
        "• Supabase (Database - Free 500MB)\n"
        "• Render (Backend - Free 750hrs/month)\n"
        "• Vercel (Frontend - Free unlimited)\n\n"
        "[bold green]Total Cost: $0/month[/bold green]",
        title="🚀 Image Captioning Deployment"
    ))
    
    if not questionary.confirm("\nReady to begin?").ask():
        console.print("Deployment cancelled.")
        return
    
    # Check prerequisites
    if not check_prerequisites():
        console.print("\nPlease install missing tools and try again.")
        return
    
    # Step 1: Supabase
    db_url = setup_supabase()
    
    # Step 2: Render
    backend_url = deploy_backend_render()
    
    # Step 3: Vercel
    frontend_url = deploy_frontend_vercel(backend_url)
    
    if not frontend_url:
        console.print("\n❌ Deployment incomplete. Please complete manually.")
        return
    
    # Step 4: Update CORS
    update_cors(backend_url, frontend_url)
    
    # Step 5: Summary
    create_summary(db_url, backend_url, frontend_url)


if __name__ == '__main__':
    # Check if required packages are installed
    try:
        import questionary
        from rich.console import Console
    except ImportError:
        print("Installing required packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'questionary', 'rich'])
        print("\nPlease run the script again.")
        sys.exit(0)
    
    main()
