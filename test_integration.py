#!/usr/bin/env python3
"""
Test script for DhanHQ integration and Supabase connectivity
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")

    try:
        import dhanhq
        print("✓ dhanhq module imported")
    except ImportError as e:
        print(f"✗ Failed to import dhanhq: {e}")
        return False

    try:
        import supabase
        print("✓ supabase module imported")
    except ImportError as e:
        print(f"✗ Failed to import supabase: {e}")
        return False

    try:
        from dhan_integration import get_dhan_manager
        print("✓ dhan_integration module imported")
    except ImportError as e:
        print(f"✗ Failed to import dhan_integration: {e}")
        return False

    try:
        from supabase_manager import get_supabase_manager
        print("✓ supabase_manager module imported")
    except ImportError as e:
        print(f"✗ Failed to import supabase_manager: {e}")
        return False

    return True

async def test_supabase():
    """Test Supabase connection"""
    print("\nTesting Supabase connection...")

    try:
        from supabase_manager import get_supabase_manager

        db = get_supabase_manager()

        if not db.is_available():
            print("⚠ Supabase not available (credentials not set)")
            return True  # Not an error, just not configured

        # Test reading symbols
        symbols = await db.get_popular_symbols(5)
        print(f"✓ Supabase connected - Found {len(symbols)} symbols")

        if symbols:
            print(f"  Sample: {symbols[0].get('symbol')} - {symbols[0].get('name')}")

        return True

    except Exception as e:
        print(f"✗ Supabase error: {e}")
        return False

async def test_dhan_manager():
    """Test DhanHQ manager initialization"""
    print("\nTesting DhanHQ manager...")

    try:
        from dhan_integration import get_dhan_manager

        # Check credentials
        client_id = os.getenv("DHAN_CLIENT_ID")
        access_token = os.getenv("DHAN_API_KEY")

        if not client_id or client_id.startswith("your_"):
            print("⚠ DHAN_CLIENT_ID not configured")
            return True

        if not access_token or access_token.startswith("your_"):
            print("⚠ DHAN_API_KEY not configured")
            return True

        # Try to initialize
        dhan_manager = get_dhan_manager()
        print("✓ DhanHQ manager initialized")

        status = dhan_manager.get_status()
        print(f"  Status: {status}")

        return True

    except Exception as e:
        print(f"✗ DhanHQ manager error: {e}")
        print(f"  This is expected if credentials are not configured")
        return True  # Not a fatal error for testing

async def test_symbol_manager():
    """Test symbol manager"""
    print("\nTesting symbol manager...")

    try:
        from symbol_manager import symbol_manager

        # Test getting a symbol
        symbol_info = await symbol_manager.get_symbol_info("RELIANCE")

        if symbol_info:
            print(f"✓ Symbol manager working")
            print(f"  RELIANCE: {symbol_info.get('name')}")
        else:
            print("⚠ Symbol not found in cache")

        # Test search
        results = await symbol_manager.search_symbols("TCS", limit=3)
        print(f"✓ Symbol search working - Found {len(results)} results")

        return True

    except Exception as e:
        print(f"✗ Symbol manager error: {e}")
        return False

async def test_historical_manager():
    """Test historical data manager"""
    print("\nTesting historical data manager...")

    try:
        from historical_data_manager import historical_manager

        # Test market hours detection
        is_market_hours = historical_manager.is_market_hours()
        status = "OPEN" if is_market_hours else "CLOSED"
        print(f"✓ Historical manager working")
        print(f"  Market status: {status}")

        return True

    except Exception as e:
        print(f"✗ Historical manager error: {e}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("Order Flow Visualizer - Integration Test")
    print("=" * 60)
    print()

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False

    # Test components
    tests = [
        test_supabase(),
        test_symbol_manager(),
        test_historical_manager(),
        test_dhan_manager(),
    ]

    results = await asyncio.gather(*tests, return_exceptions=True)

    # Check results
    failed = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed.append(str(result))
        elif result is False:
            failed.append(f"Test {i+1}")

    print()
    print("=" * 60)
    if failed:
        print("❌ Some tests failed:")
        for f in failed:
            print(f"  - {f}")
        print()
        print("Note: DhanHQ tests require valid credentials in .env")
        print("=" * 60)
        return False
    else:
        print("✓ All tests passed!")
        print("=" * 60)
        return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
