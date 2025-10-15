"""
FastAPI WebSocket bridge for DhanHQ order flow visualization
Connects to DhanHQ WebSocket feeds and streams data to frontend
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Set
from collections import defaultdict, deque

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Import dynamic symbol manager and historical data manager
from symbol_manager import symbol_manager
from historical_data_manager import historical_manager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Order Flow Visualizer API")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DHAN_API_KEY = os.getenv("DHAN_API_KEY")
DHAN_API_SECRET = os.getenv("DHAN_API_SECRET")
DHAN_WS_URL = os.getenv("DHAN_WEBSOCKET_URL", "wss://api.dhanhq.co/v2/full-market-depth/")

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
    side: str  # 'buy' or 'sell'
    timestamp: float

class AggregatedTick(BaseModel):
    price: float
    total_volume: int
    buy_volume: int
    sell_volume: int
    trade_count: int
    timestamp: float

# Global state
connected_clients: Set[WebSocket] = set()
current_symbol = "RELIANCE"  # Default symbol
dhan_websocket = None
tick_buffer = deque(maxlen=10000)  # Buffer for tick data
aggregated_data = defaultdict(lambda: defaultdict(int))  # Price -> volume aggregation
last_aggregation_time = time.time()
startup_time = time.time()  # Track startup time

# Default symbols for initial setup (will be replaced by dynamic system)
DEFAULT_SYMBOLS = {
    "RELIANCE": {"token": "2885633", "name": "RELIANCE"},
    "TCS": {"token": "2953217", "name": "TCS"},
    "HDFCBANK": {"token": "341249", "name": "HDFC BANK"},
    "INFY": {"token": "408065", "name": "INFOSYS"},
    "ITC": {"token": "424961", "name": "ITC"},
    "BHARTIARTL": {"token": "2714625", "name": "BHARTI AIRTEL"},
    "SBIN": {"token": "779521", "name": "STATE BANK OF INDIA"},
    "ASIANPAINT": {"token": "60417", "name": "ASIAN PAINTS"},
    "KOTAKBANK": {"token": "492033", "name": "KOTAK MAHINDRA BANK"},
    "MARUTI": {"token": "2815745", "name": "MARUTI SUZUKI"},
}

class DhanWebSocketClient:
    """Handles connection to DhanHQ WebSocket API"""
    
    def __init__(self):
        self.websocket = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
    async def connect(self):
        """Connect to DhanHQ WebSocket"""
        try:
            # DhanHQ uses access-token header, not Authorization Bearer
            headers = {
                "access-token": DHAN_API_KEY,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            self.websocket = await websockets.connect(
                DHAN_WS_URL,
                extra_headers=headers,
                ping_interval=20,
                ping_timeout=10
            )
            self.connected = True
            self.reconnect_attempts = 0
            logger.info("Connected to DhanHQ WebSocket")
            
            # Subscribe to market depth
            await self.subscribe_market_depth()
            
        except Exception as e:
            logger.error(f"Failed to connect to DhanHQ: {e}")
            self.connected = False
            await self.handle_reconnect()
    
    async def subscribe_market_depth(self):
        """Subscribe to market depth feed"""
        if not self.connected:
            return
            
        # Try dynamic symbol manager first, then fallback to default symbols
        symbol_info = await symbol_manager.get_symbol_info(current_symbol)
        if not symbol_info:
            symbol_info = DEFAULT_SYMBOLS.get(current_symbol)
        
        if not symbol_info:
            logger.error(f"Unknown symbol: {current_symbol}")
            return
            
        # DhanHQ WebSocket subscription format
        subscribe_msg = {
            "action": "subscribe",
            "instrument_token": symbol_info["token"],
            "feed_type": "full_market_depth",
            "dhanClientId": os.getenv("DHAN_CLIENT_ID", ""),
            "segment": "NSE_EQ"  # NSE Equity segment
        }
        
        await self.websocket.send(json.dumps(subscribe_msg))
        logger.info(f"Subscribed to market depth for {current_symbol}")
    
    async def handle_reconnect(self):
        """Handle reconnection logic"""
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            wait_time = min(2 ** self.reconnect_attempts, 30)
            logger.info(f"Reconnecting in {wait_time} seconds... (attempt {self.reconnect_attempts})")
            await asyncio.sleep(wait_time)
            await self.connect()
        else:
            logger.error("Max reconnection attempts reached")
    
    async def listen(self):
        """Listen for incoming messages from DhanHQ"""
        while self.connected:
            try:
                message = await self.websocket.recv()
                await self.process_message(message)
            except websockets.exceptions.ConnectionClosed:
                logger.warning("DhanHQ WebSocket connection closed")
                self.connected = False
                await self.handle_reconnect()
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def process_message(self, message: str):
        """Process incoming message from DhanHQ"""
        try:
            data = json.loads(message)
            
            # DhanHQ WebSocket message types
            message_type = data.get("type", "")
            
            if message_type == "market_depth":
                await self.process_market_depth(data)
            elif message_type == "tick":
                await self.process_tick(data)
            elif message_type == "quote":
                await self.process_quote(data)
            elif message_type == "error":
                logger.error(f"DhanHQ WebSocket error: {data.get('message', 'Unknown error')}")
            else:
                logger.debug(f"Received message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def process_market_depth(self, data: dict):
        """Process market depth update"""
        try:
            # DhanHQ market depth data structure
            depth_update = MarketDepthUpdate(
                type="depth_update",
                instrument_token=data.get("instrument_token", ""),
                bids=data.get("bids", []),
                asks=data.get("asks", []),
                last_trade=data.get("last_trade"),
                timestamp=time.time()
            )
            
            # Broadcast to connected clients
            await broadcast_to_clients(depth_update.dict())
            
        except Exception as e:
            logger.error(f"Error processing market depth: {e}")
    
    async def process_quote(self, data: dict):
        """Process quote data"""
        try:
            # DhanHQ quote data structure
            quote_data = {
                "type": "quote_update",
                "instrument_token": data.get("instrument_token", ""),
                "ltp": data.get("ltp", 0.0),
                "change": data.get("change", 0.0),
                "change_percent": data.get("change_percent", 0.0),
                "volume": data.get("volume", 0),
                "timestamp": time.time()
            }
            
            # Broadcast to connected clients
            await broadcast_to_clients(quote_data)
            
        except Exception as e:
            logger.error(f"Error processing quote: {e}")
    
    async def process_tick(self, data: dict):
        """Process tick data"""
        try:
            trade_data = TradeData(
                price=data.get("price", 0.0),
                quantity=data.get("quantity", 0),
                side=data.get("side", "unknown"),
                timestamp=time.time()
            )
            
            # Add to tick buffer
            tick_buffer.append(trade_data.dict())
            
            # Aggregate ticks
            await aggregate_ticks()
            
        except Exception as e:
            logger.error(f"Error processing tick: {e}")
    
    async def disconnect(self):
        """Disconnect from DhanHQ WebSocket"""
        if self.websocket:
            await self.websocket.close()
        self.connected = False

# Global DhanHQ client
dhan_client = DhanWebSocketClient()

async def aggregate_ticks():
    """Aggregate ticks for smooth visualization"""
    global last_aggregation_time
    
    current_time = time.time()
    if current_time - last_aggregation_time < 0.1:  # 100ms aggregation window
        return
    
    # Process ticks in buffer
    aggregated_trades = {}
    
    for tick in list(tick_buffer):
        price = tick["price"]
        quantity = tick["quantity"]
        side = tick["side"]
        
        if price not in aggregated_trades:
            aggregated_trades[price] = {
                "total_volume": 0,
                "buy_volume": 0,
                "sell_volume": 0,
                "trade_count": 0,
                "timestamp": current_time
            }
        
        aggregated_trades[price]["total_volume"] += quantity
        aggregated_trades[price]["trade_count"] += 1
        
        if side == "buy":
            aggregated_trades[price]["buy_volume"] += quantity
        else:
            aggregated_trades[price]["sell_volume"] += quantity
    
    # Clear buffer
    tick_buffer.clear()
    last_aggregation_time = current_time
    
    # Broadcast aggregated data
    if aggregated_trades:
        await broadcast_to_clients({
            "type": "aggregated_trades",
            "data": aggregated_trades,
            "timestamp": current_time
        })

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
    
    # Remove disconnected clients
    connected_clients -= disconnected_clients

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for frontend connection"""
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(connected_clients)}")
    
    # Check market status and send initial data
    is_market_hours = historical_manager.is_market_hours()
    await websocket.send_text(json.dumps({
        "type": "market_status",
        "is_market_hours": is_market_hours,
        "market_status": "open" if is_market_hours else "closed"
    }))
    
    # If market is closed, send historical data
    if not is_market_hours:
        try:
            historical_data = await historical_manager.get_off_market_data(current_symbol, "1min")
            if "error" not in historical_data:
                await websocket.send_text(json.dumps(historical_data))
        except Exception as e:
            logger.error(f"Error sending historical data: {e}")
    
    try:
        while True:
            # Keep connection alive and handle client messages
            message = await websocket.receive_text()
            data = json.loads(message)
            
            # Handle ping/pong for connection health
            if data.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": time.time()
                }))
                continue
            
            # Handle symbol change requests
            if data.get("type") == "change_symbol":
                global current_symbol
                new_symbol = data.get("symbol")
                
                # Try to get symbol info dynamically first
                symbol_info = await symbol_manager.get_symbol_info(new_symbol)
                if symbol_info:
                    current_symbol = new_symbol
                    
                    # Check if market is open for live data
                    if is_market_hours:
                        await dhan_client.subscribe_market_depth()
                        await websocket.send_text(json.dumps({
                            "type": "symbol_changed",
                            "symbol": new_symbol,
                            "source": "dynamic",
                            "symbol_info": symbol_info,
                            "data_mode": "live"
                        }))
                    else:
                        # Send historical data for off-market
                        historical_data = await historical_manager.get_off_market_data(new_symbol, "1min")
                        if "error" not in historical_data:
                            await websocket.send_text(json.dumps(historical_data))
                        
                        await websocket.send_text(json.dumps({
                            "type": "symbol_changed",
                            "symbol": new_symbol,
                            "source": "dynamic",
                            "symbol_info": symbol_info,
                            "data_mode": "historical"
                        }))
                else:
                    # Fallback to default symbols
                    if new_symbol in DEFAULT_SYMBOLS:
                        current_symbol = new_symbol
                        
                        if is_market_hours:
                            await dhan_client.subscribe_market_depth()
                            await websocket.send_text(json.dumps({
                                "type": "symbol_changed",
                                "symbol": new_symbol,
                                "source": "default",
                                "symbol_info": DEFAULT_SYMBOLS[new_symbol],
                                "data_mode": "live"
                            }))
                        else:
                            # Send historical data for off-market
                            historical_data = await historical_manager.get_off_market_data(new_symbol, "1min")
                            if "error" not in historical_data:
                                await websocket.send_text(json.dumps(historical_data))
                            
                            await websocket.send_text(json.dumps({
                                "type": "symbol_changed",
                                "symbol": new_symbol,
                                "source": "default",
                                "symbol_info": DEFAULT_SYMBOLS[new_symbol],
                                "data_mode": "historical"
                            }))
                    else:
                        await websocket.send_text(json.dumps({
                            "type": "symbol_error",
                            "symbol": new_symbol,
                            "message": "Symbol not found. Please check the symbol name or try searching for it first."
                        }))
            
            # Handle timeframe change for historical data
            if data.get("type") == "change_timeframe":
                if not is_market_hours:
                    timeframe = data.get("timeframe", "1min")
                    historical_data = await historical_manager.get_off_market_data(current_symbol, timeframe)
                    if "error" not in historical_data:
                        await websocket.send_text(json.dumps(historical_data))
            
            # Handle symbol search requests
            if data.get("type") == "search_symbols":
                query = data.get("query", "")
                limit = data.get("limit", 20)
                results = await symbol_manager.search_symbols(query, limit)
                await websocket.send_text(json.dumps({
                    "type": "symbol_search_results",
                    "query": query,
                    "results": results
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
        "status": "running",
        "connected_clients": len(connected_clients),
        "current_symbol": current_symbol,
        "dhan_connected": dhan_client.connected,
        "api_configured": bool(DHAN_API_KEY and DHAN_API_SECRET),
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy" if dhan_client.connected else "degraded",
        "backend": "running",
        "dhan_connection": "connected" if dhan_client.connected else "disconnected",
        "clients_connected": len(connected_clients),
        "current_symbol": current_symbol,
        "tick_buffer_size": len(tick_buffer),
        "uptime": time.time() - startup_time,
        "api_configured": bool(DHAN_API_KEY and DHAN_API_SECRET)
    }

@app.get("/symbols")
async def get_symbols():
    """Get available symbols (deprecated - use /symbols/dynamic instead)"""
    return {"symbols": list(DEFAULT_SYMBOLS.keys()), "note": "Use /symbols/dynamic for full symbol list"}

@app.get("/symbols/dynamic")
async def get_dynamic_symbols():
    """Get dynamically discovered symbols"""
    cached_symbols = symbol_manager.get_cached_symbols()
    return {
        "symbols": list(cached_symbols.keys()),
        "count": len(cached_symbols),
        "last_updated": symbol_manager.last_update
    }

@app.get("/symbols/search")
async def search_symbols(q: str, limit: int = 20):
    """Search symbols by name or symbol"""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    results = await symbol_manager.search_symbols(q, limit)
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }

@app.get("/symbols/popular")
async def get_popular_symbols(limit: int = 50):
    """Get most popular/traded symbols"""
    results = await symbol_manager.get_popular_symbols(limit)
    return {
        "symbols": results,
        "count": len(results)
    }

@app.post("/symbols/request")
async def request_symbol(symbol: str):
    """Request a new symbol to be added"""
    symbol = symbol.upper()
    
    # Check if already exists
    if symbol in symbol_manager.get_cached_symbols():
        return {"message": f"Symbol {symbol} already exists", "status": "exists"}
    
    # Try to fetch symbol info
    symbol_info = await symbol_manager.get_symbol_info(symbol)
    if symbol_info:
        return {
            "message": f"Symbol {symbol} added successfully",
            "status": "added",
            "symbol_info": symbol_info
        }
    else:
        return {
            "message": f"Symbol {symbol} not found. Added to pending requests.",
            "status": "pending"
        }

@app.get("/symbols/info/{symbol}")
async def get_symbol_info(symbol: str):
    """Get detailed information about a symbol"""
    symbol = symbol.upper()
    symbol_info = await symbol_manager.get_symbol_info(symbol)
    
    if not symbol_info:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    return {
        "symbol": symbol,
        "info": symbol_info
    }

@app.get("/market/status")
async def get_market_status():
    """Get current market status and hours"""
    is_market_hours = historical_manager.is_market_hours()
    now = datetime.now()
    
    return {
        "is_market_hours": is_market_hours,
        "current_time": now.isoformat(),
        "market_status": "open" if is_market_hours else "closed",
        "next_market_open": "09:15 AM" if not is_market_hours else None
    }

@app.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str, 
    timeframe: str = "1min", 
    days: int = 1
):
    """Get historical data for off-market visualization"""
    symbol = symbol.upper()
    
    # Validate timeframe
    valid_timeframes = ["1min", "5min", "15min", "1hour", "1day"]
    if timeframe not in valid_timeframes:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid timeframe. Must be one of: {valid_timeframes}"
        )
    
    # Get historical data
    data = await historical_manager.get_off_market_data(symbol, timeframe)
    
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    
    return data

@app.get("/off-market/{symbol}")
async def get_off_market_visualization(symbol: str, timeframe: str = "1min"):
    """Get comprehensive off-market data for visualization"""
    symbol = symbol.upper()
    
    try:
        data = await historical_manager.get_off_market_data(symbol, timeframe)
        
        if "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        
        # Broadcast to connected clients
        await broadcast_to_clients(data)
        
        return data
        
    except Exception as e:
        logger.error(f"Error getting off-market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize DhanHQ connection on startup"""
    logger.info("Starting Order Flow Visualizer backend...")
    
    # Validate environment variables
    if not DHAN_API_KEY or not DHAN_API_SECRET:
        logger.error("DhanHQ API credentials not found in environment variables")
        logger.error("Please set DHAN_API_KEY and DHAN_API_SECRET in your .env file")
        return
    
    # Start DhanHQ connection
    asyncio.create_task(dhan_client.connect())
    asyncio.create_task(dhan_client.listen())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    await dhan_client.disconnect()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
