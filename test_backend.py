#!/usr/bin/env python3
"""
Test script to verify backend functionality
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic Python modules
        import asyncio
        import json
        import logging
        import time
        from datetime import datetime
        from typing import Dict, List, Optional, Set
        from collections import defaultdict, deque
        print("✅ Basic Python modules imported successfully")
        
        # Test external dependencies
        try:
            import websockets
            print("✅ websockets imported successfully")
        except ImportError:
            print("❌ websockets not installed - run: pip install websockets")
            return False
            
        try:
            from fastapi import FastAPI, WebSocket, WebSocketDisconnect
            from fastapi.middleware.cors import CORSMiddleware
            print("✅ FastAPI imported successfully")
        except ImportError:
            print("❌ FastAPI not installed - run: pip install fastapi")
            return False
            
        try:
            from pydantic import BaseModel
            print("✅ Pydantic imported successfully")
        except ImportError:
            print("❌ Pydantic not installed - run: pip install pydantic")
            return False
            
        try:
            import uvicorn
            print("✅ Uvicorn imported successfully")
        except ImportError:
            print("❌ Uvicorn not installed - run: pip install uvicorn")
            return False
            
        try:
            from dotenv import load_dotenv
            print("✅ python-dotenv imported successfully")
        except ImportError:
            print("❌ python-dotenv not installed - run: pip install python-dotenv")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\nTesting environment...")
    
    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found - copy env.example to .env")
        print("   cp env.example .env")
    
    # Check if backend directory exists
    if backend_dir.exists():
        print("✅ Backend directory found")
    else:
        print("❌ Backend directory not found")
        return False
    
    # Check if main.py exists
    main_file = backend_dir / "main.py"
    if main_file.exists():
        print("✅ main.py found")
    else:
        print("❌ main.py not found")
        return False
    
    return True

def test_backend_syntax():
    """Test if backend code has valid syntax"""
    print("\nTesting backend syntax...")
    
    try:
        # Try to compile the main.py file
        main_file = backend_dir / "main.py"
        with open(main_file, 'r') as f:
            code = f.read()
        
        compile(code, str(main_file), 'exec')
        print("✅ Backend syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in backend: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Order Flow Visualizer Backend")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Backend Syntax", test_backend_syntax),
        ("Dependencies", test_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready to run.")
        print("\n🚀 To start the backend:")
        print("   python start_backend.py")
        print("   OR")
        print("   cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\n💡 Quick fixes:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Copy environment file: cp env.example .env")
        print("   3. Add your DhanHQ API credentials to .env")

if __name__ == "__main__":
    main()
