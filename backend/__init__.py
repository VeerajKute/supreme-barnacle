"""
Order Flow Visualizer Backend Package

This package contains the FastAPI backend for the real-time order flow visualizer.
It provides WebSocket connections to DhanHQ APIs and dynamic symbol discovery.

Modules:
    main: FastAPI application with WebSocket endpoints
    symbol_manager: Dynamic symbol discovery and caching system

Features:
    - Real-time market data streaming
    - Dynamic symbol discovery
    - WebSocket bridge to frontend
    - SQLite caching for symbols
    - Auto-reconnection with exponential backoff
"""

__version__ = "1.0.0"
__author__ = "Order Flow Visualizer Team"
__description__ = "Real-time order flow visualizer for Indian equities"

# Import main components for easy access
from .main import app, dhan_client, symbol_manager
from .symbol_manager import SymbolManager

__all__ = [
    "app",
    "dhan_client", 
    "symbol_manager",
    "SymbolManager"
]
