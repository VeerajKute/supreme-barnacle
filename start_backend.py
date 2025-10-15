#!/usr/bin/env python3
"""
Startup script for the Order Flow Visualizer backend
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("🚀 Starting Order Flow Visualizer Backend...")
    print("📍 Backend directory:", backend_dir.absolute())
    print("🔗 WebSocket endpoint: ws://localhost:8000/ws")
    print("📊 API endpoint: http://localhost:8000")
    print("=" * 50)
    
    try:
        # Start the FastAPI server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
