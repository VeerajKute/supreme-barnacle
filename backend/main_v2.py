"""
FastAPI WebSocket bridge for DhanHQ order flow visualization
Uses official dhanhq Python SDK for market data
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Set
from collections import defaultdict, deque

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Import managers
from symbol_manager import symbol_manager
from historical_data_manager import historical_manager
from dhan_integration import get_dhan_manager
from supabase_manager import get_supabase_manager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Order Flow Visualizer API v2")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class MarketDepthUpdate(BaseModel):
    type: str
    instrument_token: str
    bids: List[List[float]]
    asks: List[List[float]]
    last_trade: Optional[Dict]
    timestamp: float

class TradeData(BaseModel):
    price: float
    quantity: int
    side: str
    timestamp: float

# Global state
connected_clients: Set[WebSocket] = set()
current_symbol = "RELIANCE"
current_security_id = "2885633"
tick_buffer = deque(maxlen=10000)
last_aggregation_time = time.time()
startup_time = time.time()

# Initialize managers
dhan_manager = None
supabase_manager = None

async def broadcast_to_clients(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    if not connected_clients:
        return

    message_str = json.dumps(message)
    disconnected_clients = set()

    for client in connected_clients:
        try:
            await client.send_text(message_str)
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
            disconnected_clients.add(client)

    connected_clients -= disconnected_clients

async def handle_depth_update(data: Dict):
    """Handle market depth updates from DhanHQ"""
    try:
        await broadcast_to_clients(data)

        # Save to database if available
        if supabase_manager and supabase_manager.is_available():
            await supabase_manager.save_market_data({
                'symbol': current_symbol,
                'timestamp': data.get('timestamp'),
                'ltp': data.get('ltp'),
                'volume': data.get('volume'),
                'bid_price': data.get('bids', [[0]])[0][0] if data.get('bids') else None,
                'ask_price': data.get('asks', [[0]])[0][0] if data.get('asks') else None,
            })

    except Exception as e:
        logger.error(f"Error handling depth update: {e}")

async def handle_ticker_update(data: Dict):
    """Handle ticker updates from DhanHQ"""
    try:
        await broadcast_to_clients(data)
    except Exception as e:
        logger.error(f"Error handling ticker update: {e}")

async def handle_trade_update(data: Dict):
    """Handle trade updates from DhanHQ"""
    try:
        # Add to tick buffer
        tick_buffer.append(data)

        # Aggregate and broadcast
        await aggregate_ticks()

    except Exception as e:
        logger.error(f"Error handling trade update: {e}")

async def aggregate_ticks():
    """Aggregate ticks for smooth visualization"""
    global last_aggregation_time

    current_time = time.time()
    if current_time - last_aggregation_time < 0.1:  # 100ms window
        return

    if not tick_buffer:
        return

    # Process ticks
    aggregated_trades = {}

    for tick in list(tick_buffer):
        price = tick.get('price', 0)
        quantity = tick.get('quantity', 0)
        timestamp = tick.get('timestamp', current_time)

        if price not in aggregated_trades:
            aggregated_trades[price] = {
                'total_volume': 0,
                'buy_volume': 0,
                'sell_volume': 0,
                'trade_count': 0,
                'timestamp': timestamp
            }

        aggregated_trades[price]['total_volume'] += quantity
        aggregated_trades[price]['trade_count'] += 1

        # Simple heuristic for buy/sell (can be improved with actual data)
        aggregated_trades[price]['buy_volume'] += quantity // 2
        aggregated_trades[price]['sell_volume'] += quantity - (quantity // 2)

    tick_buffer.clear()
    last_aggregation_time = current_time

    if aggregated_trades:
        await broadcast_to_clients({
            'type': 'aggregated_trades',
            'data': aggregated_trades,
            'timestamp': current_time
        })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for frontend connection"""
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(connected_clients)}")

    # Check market status
    is_market_hours = historical_manager.is_market_hours()
    await websocket.send_text(json.dumps({
        'type': 'market_status',
        'is_market_hours': is_market_hours,
        'market_status': 'open' if is_market_hours else 'closed'
    }))

    # Send initial data based on market status
    if not is_market_hours:
        try:
            historical_data = await historical_manager.get_off_market_data(current_symbol, "1min")
            if 'error' not in historical_data:
                await websocket.send_text(json.dumps(historical_data))
        except Exception as e:
            logger.error(f"Error sending historical data: {e}")

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            # Handle ping/pong
            if data.get('type') == 'ping':
                await websocket.send_text(json.dumps({
                    'type': 'pong',
                    'timestamp': time.time()
                }))
                continue

            # Handle symbol change
            if data.get('type') == 'change_symbol':
                global current_symbol, current_security_id
                new_symbol = data.get('symbol', '').upper()

                # Get symbol info from database first, then cache
                symbol_info = None
                if supabase_manager and supabase_manager.is_available():
                    symbol_info = await supabase_manager.get_symbol(new_symbol)

                if not symbol_info:
                    symbol_info = await symbol_manager.get_symbol_info(new_symbol)

                if symbol_info:
                    current_symbol = new_symbol
                    current_security_id = symbol_info.get('token', '')

                    # Update search count in database
                    if supabase_manager and supabase_manager.is_available():
                        await supabase_manager.save_symbol({
                            **symbol_info,
                            'symbol': new_symbol
                        })

                    # Subscribe to new symbol if market is open
                    if is_market_hours and dhan_manager:
                        try:
                            dhan_manager.subscribe_symbol(
                                security_id=current_security_id,
                                symbol=new_symbol,
                                exchange_segment=1  # NSE
                            )

                            await websocket.send_text(json.dumps({
                                'type': 'symbol_changed',
                                'symbol': new_symbol,
                                'symbol_info': symbol_info,
                                'data_mode': 'live'
                            }))

                        except Exception as e:
                            logger.error(f"Error subscribing to symbol: {e}")
                            await websocket.send_text(json.dumps({
                                'type': 'symbol_error',
                                'symbol': new_symbol,
                                'message': f"Error subscribing: {str(e)}"
                            }))
                    else:
                        # Send historical data for off-market
                        historical_data = await historical_manager.get_off_market_data(new_symbol, "1min")
                        if 'error' not in historical_data:
                            await websocket.send_text(json.dumps(historical_data))

                        await websocket.send_text(json.dumps({
                            'type': 'symbol_changed',
                            'symbol': new_symbol,
                            'symbol_info': symbol_info,
                            'data_mode': 'historical'
                        }))
                else:
                    await websocket.send_text(json.dumps({
                        'type': 'symbol_error',
                        'symbol': new_symbol,
                        'message': 'Symbol not found'
                    }))

            # Handle timeframe change
            if data.get('type') == 'change_timeframe':
                if not is_market_hours:
                    timeframe = data.get('timeframe', '1min')
                    historical_data = await historical_manager.get_off_market_data(current_symbol, timeframe)
                    if 'error' not in historical_data:
                        await websocket.send_text(json.dumps(historical_data))

            # Handle symbol search
            if data.get('type') == 'search_symbols':
                query = data.get('query', '')
                limit = data.get('limit', 20)

                results = []
                if supabase_manager and supabase_manager.is_available():
                    results = await supabase_manager.search_symbols(query, limit)

                if not results:
                    results = await symbol_manager.search_symbols(query, limit)

                await websocket.send_text(json.dumps({
                    'type': 'symbol_search_results',
                    'query': query,
                    'results': results
                }))

    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connected_clients.discard(websocket)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        'status': 'running',
        'version': '2.0',
        'connected_clients': len(connected_clients),
        'current_symbol': current_symbol,
        'dhan_connected': dhan_manager.get_status()['connected'] if dhan_manager else False,
        'supabase_available': supabase_manager.is_available() if supabase_manager else False,
        'timestamp': time.time()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    dhan_status = dhan_manager.get_status() if dhan_manager else {'connected': False}

    return {
        'status': 'healthy',
        'backend': 'running',
        'dhan_connection': dhan_status,
        'clients_connected': len(connected_clients),
        'current_symbol': current_symbol,
        'supabase_available': supabase_manager.is_available() if supabase_manager else False,
        'uptime': time.time() - startup_time
    }

@app.get("/symbols/dynamic")
async def get_dynamic_symbols():
    """Get dynamically discovered symbols"""
    if supabase_manager and supabase_manager.is_available():
        symbols = await supabase_manager.get_popular_symbols(100)
        return {
            'symbols': [s['symbol'] for s in symbols],
            'count': len(symbols),
            'source': 'database'
        }

    cached_symbols = symbol_manager.get_cached_symbols()
    return {
        'symbols': list(cached_symbols.keys()),
        'count': len(cached_symbols),
        'source': 'cache'
    }

@app.get("/symbols/search")
async def search_symbols(q: str, limit: int = 20):
    """Search symbols"""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    results = []
    if supabase_manager and supabase_manager.is_available():
        results = await supabase_manager.search_symbols(q, limit)

    if not results:
        results = await symbol_manager.search_symbols(q, limit)

    return {
        'query': q,
        'results': results,
        'count': len(results)
    }

@app.get("/symbols/popular")
async def get_popular_symbols(limit: int = 50):
    """Get popular symbols"""
    if supabase_manager and supabase_manager.is_available():
        results = await supabase_manager.get_popular_symbols(limit)
    else:
        results = await symbol_manager.get_popular_symbols(limit)

    return {
        'symbols': results,
        'count': len(results)
    }

@app.get("/market/status")
async def get_market_status():
    """Get market status"""
    is_market_hours = historical_manager.is_market_hours()
    now = datetime.now()

    return {
        'is_market_hours': is_market_hours,
        'current_time': now.isoformat(),
        'market_status': 'open' if is_market_hours else 'closed',
        'next_market_open': '09:15 AM' if not is_market_hours else None
    }

@app.get("/historical/{symbol}")
async def get_historical_data(symbol: str, timeframe: str = "1min", days: int = 1):
    """Get historical data"""
    symbol = symbol.upper()

    valid_timeframes = ["1min", "5min", "15min", "1hour", "1day"]
    if timeframe not in valid_timeframes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timeframe. Must be one of: {valid_timeframes}"
        )

    data = await historical_manager.get_off_market_data(symbol, timeframe)

    if 'error' in data:
        raise HTTPException(status_code=404, detail=data['error'])

    return data

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    global dhan_manager, supabase_manager

    logger.info("Starting Order Flow Visualizer v2...")

    # Initialize Supabase
    try:
        supabase_manager = get_supabase_manager()
        if supabase_manager.is_available():
            logger.info("Supabase database connected")
        else:
            logger.warning("Supabase not available, using local cache only")
    except Exception as e:
        logger.error(f"Error initializing Supabase: {e}")

    # Initialize DhanHQ
    try:
        dhan_manager = get_dhan_manager()

        # Set up callbacks
        dhan_manager.set_depth_callback(handle_depth_update)
        dhan_manager.set_ticker_callback(handle_ticker_update)
        dhan_manager.set_trade_callback(handle_trade_update)

        # Subscribe to default symbol
        symbol_info = await symbol_manager.get_symbol_info(current_symbol)
        if symbol_info:
            dhan_manager.subscribe_symbol(
                security_id=symbol_info.get('token', current_security_id),
                symbol=current_symbol,
                exchange_segment=1
            )

        logger.info(f"DhanHQ manager initialized for {current_symbol}")

    except Exception as e:
        logger.error(f"Error initializing DhanHQ: {e}")
        logger.error("Market data features will be limited")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")

    if dhan_manager:
        dhan_manager.unsubscribe()

if __name__ == "__main__":
    uvicorn.run(
        "main_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
