#!/usr/bin/env python3
"""
Run local frontend server without Docker.
Simple HTTP server for the HTML/JS frontend.
"""

import os
import sys
import http.server
import socketserver
import webbrowser
from pathlib import Path
import time
import threading

project_root = Path(__file__).parent.parent
frontend_dir = project_root / "frontend_simple"

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with CORS enabled."""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def open_browser():
    """Open browser after a short delay."""
    time.sleep(2)
    print("\n🌐 Opening browser...")
    webbrowser.open('http://localhost:3000')

def main():
    print("\n" + "="*60)
    print("  🚀 STARTING FRONTEND SERVER (NO DOCKER)")
    print("="*60 + "\n")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    PORT = 3000
    
    print("="*60)
    print("  ✅ FRONTEND STARTING...")
    print("="*60)
    print(f"\n  🌐 Frontend URL: http://localhost:{PORT}")
    print(f"  📂 Serving from: {frontend_dir}")
    print(f"\n  Make sure backend is running on port 8000!")
    print(f"  Press Ctrl+C to stop\n")
    print("="*60 + "\n")
    
    # Open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    try:
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            print(f"✅ Serving at http://localhost:{PORT}\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Frontend server stopped.")
    except OSError as e:
        if "address already in use" in str(e).lower():
            print(f"\n❌ Port {PORT} is already in use!")
            print("Solution: Close any other app using port 3000")
        else:
            print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
