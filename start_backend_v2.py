#!/usr/bin/env python3
"""
Startup script for Order Flow Visualizer backend v2
Uses official DhanHQ SDK and Supabase integration
"""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("dhanhq", "DhanHQ SDK"),
        ("supabase", "Supabase"),
        ("dotenv", "python-dotenv"),
    ]

    missing = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✓ {name} is installed")
        except ImportError:
            missing.append((package, name))
            print(f"✗ {name} is NOT installed")

    if missing:
        print("\n⚠️  Missing dependencies detected!")
        print("Install them with:")
        print(f"pip install {' '.join(pkg for pkg, _ in missing)}")
        return False

    return True

def check_env_vars():
    """Check if required environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = [
        ("DHAN_CLIENT_ID", "DhanHQ Client ID"),
        ("DHAN_API_KEY", "DhanHQ Access Token"),
    ]

    optional_vars = [
        ("VITE_SUPABASE_URL", "Supabase URL"),
        ("VITE_SUPABASE_SUPABASE_ANON_KEY", "Supabase Anon Key"),
    ]

    missing = []
    for var, name in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_"):
            missing.append((var, name))
            print(f"✗ {name} ({var}) is NOT set")
        else:
            print(f"✓ {name} is configured")

    for var, name in optional_vars:
        value = os.getenv(var)
        if value and not value.startswith("your_"):
            print(f"✓ {name} is configured")
        else:
            print(f"⚠ {name} is not configured (optional)")

    if missing:
        print("\n⚠️  Missing required environment variables!")
        print("Please update your .env file with:")
        for var, name in missing:
            print(f"  {var}=<your_{var.lower()}>")
        return False

    return True

def main():
    """Main startup function"""
    print("=" * 60)
    print("Order Flow Visualizer - Backend v2")
    print("=" * 60)
    print()

    print("Step 1: Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)

    print("\nStep 2: Checking environment variables...")
    if not check_env_vars():
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ All checks passed! Starting backend server...")
    print("=" * 60)
    print()
    print("Backend will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("WebSocket endpoint: ws://localhost:8000/ws")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()

    # Import and run uvicorn
    import uvicorn

    try:
        uvicorn.run(
            "main_v2:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        print(f"\n\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
