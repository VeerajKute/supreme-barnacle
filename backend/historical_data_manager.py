"""
Historical Data Manager for Off-Market Hours
Fetches and processes historical data when live market data is unavailable
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HistoricalCandle:
    """Historical candle data structure"""
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    ohlc: List[float]  # [open, high, low, close]
    
@dataclass
class VolumeProfile:
    """Volume profile data for order flow analysis"""
    price: float
    volume: int
    buy_volume: int
    sell_volume: int
    timestamp: float

class HistoricalDataManager:
    """Manages historical data for off-market visualization"""
    
    def __init__(self):
        self.api_key = os.getenv("DHAN_API_KEY", "")
        self.base_url = "https://api.dhan.co/v2"
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
        
    async def get_historical_data(
        self, 
        symbol: str, 
        timeframe: str = "1min",
        days: int = 1
    ) -> List[HistoricalCandle]:
        """Fetch historical data from DhanHQ API"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{timeframe}_{days}"
            if cache_key in self.cache:
                cached_data, cache_time = self.cache[cache_key]
                if time.time() - cache_time < self.cache_duration:
                    return cached_data
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch from DhanHQ API
            url = f"{self.base_url}/historical"
            headers = {
                "access-token": self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            params = {
                "symbol": symbol,
                "segment": "NSE_EQ",
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "period": timeframe
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        candles = self._parse_historical_data(data)
                        
                        # Cache the data
                        self.cache[cache_key] = (candles, time.time())
                        return candles
                    else:
                        logger.error(f"Failed to fetch historical data: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return []
    
    def _parse_historical_data(self, data: dict) -> List[HistoricalCandle]:
        """Parse DhanHQ historical data response"""
        candles = []
        
        try:
            if 'data' in data and data['data']:
                for item in data['data']:
                    candle = HistoricalCandle(
                        timestamp=self._parse_timestamp(item.get('timestamp', '')),
                        open=float(item.get('open', 0)),
                        high=float(item.get('high', 0)),
                        low=float(item.get('low', 0)),
                        close=float(item.get('close', 0)),
                        volume=int(item.get('volume', 0)),
                        ohlc=[
                            float(item.get('open', 0)),
                            float(item.get('high', 0)),
                            float(item.get('low', 0)),
                            float(item.get('close', 0))
                        ]
                    )
                    candles.append(candle)
                    
        except Exception as e:
            logger.error(f"Error parsing historical data: {e}")
            
        return candles
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """Parse timestamp string to Unix timestamp"""
        try:
            if timestamp_str:
                # Handle different timestamp formats
                if 'T' in timestamp_str:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                return dt.timestamp()
        except Exception as e:
            logger.error(f"Error parsing timestamp {timestamp_str}: {e}")
        
        return time.time()
    
    async def generate_volume_profile(self, candles: List[HistoricalCandle]) -> List[VolumeProfile]:
        """Generate volume profile from historical candles"""
        volume_profile = []
        
        try:
            for candle in candles:
                # Estimate buy/sell volume based on price movement
                if candle.close > candle.open:
                    # Green candle - more buying
                    buy_volume = int(candle.volume * 0.7)
                    sell_volume = candle.volume - buy_volume
                elif candle.close < candle.open:
                    # Red candle - more selling
                    sell_volume = int(candle.volume * 0.7)
                    buy_volume = candle.volume - sell_volume
                else:
                    # Doji - equal volume
                    buy_volume = candle.volume // 2
                    sell_volume = candle.volume - buy_volume
                
                profile = VolumeProfile(
                    price=candle.close,
                    volume=candle.volume,
                    buy_volume=buy_volume,
                    sell_volume=sell_volume,
                    timestamp=candle.timestamp
                )
                volume_profile.append(profile)
                
        except Exception as e:
            logger.error(f"Error generating volume profile: {e}")
            
        return volume_profile
    
    async def simulate_order_flow(self, candles: List[HistoricalCandle]) -> List[Dict]:
        """Simulate order flow data from historical candles"""
        order_flow = []
        
        try:
            for candle in candles:
                # Simulate tick data within each candle
                ticks_per_candle = min(candle.volume // 100, 50)  # Limit ticks
                
                for i in range(ticks_per_candle):
                    # Interpolate price within OHLC range
                    price_range = candle.high - candle.low
                    if price_range > 0:
                        price = candle.low + (price_range * (i / ticks_per_candle))
                    else:
                        price = candle.close
                    
                    # Simulate buy/sell based on candle direction
                    if candle.close > candle.open:
                        side = "buy" if i % 3 != 0 else "sell"
                    else:
                        side = "sell" if i % 3 != 0 else "buy"
                    
                    # Simulate quantity
                    quantity = max(1, candle.volume // ticks_per_candle)
                    
                    tick = {
                        "type": "tick",
                        "price": round(price, 2),
                        "quantity": quantity,
                        "side": side,
                        "timestamp": candle.timestamp + (i * 0.1)  # Spread ticks within candle
                    }
                    order_flow.append(tick)
                    
        except Exception as e:
            logger.error(f"Error simulating order flow: {e}")
            
        return order_flow
    
    def is_market_hours(self) -> bool:
        """Check if current time is within market hours"""
        now = datetime.now()
        current_time = now.time()
        
        # NSE market hours: 9:15 AM - 3:30 PM (Monday to Friday)
        market_start = datetime.strptime("09:15", "%H:%M").time()
        market_end = datetime.strptime("15:30", "%H:%M").time()
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
            
        return market_start <= current_time <= market_end
    
    async def get_off_market_data(self, symbol: str, timeframe: str = "1min") -> Dict:
        """Get comprehensive off-market data for visualization"""
        try:
            # Determine data range based on timeframe
            days_map = {
                "1min": 1,
                "5min": 3,
                "15min": 7,
                "1hour": 30,
                "1day": 365
            }
            
            days = days_map.get(timeframe, 1)
            
            # Fetch historical data
            candles = await self.get_historical_data(symbol, timeframe, days)
            
            if not candles:
                return {"error": "No historical data available"}
            
            # Generate derived data
            volume_profile = await self.generate_volume_profile(candles)
            order_flow = await self.simulate_order_flow(candles)
            
            # Create market depth simulation
            market_depth = self._simulate_market_depth(candles[-1] if candles else None)
            
            return {
                "type": "off_market_data",
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": [self._candle_to_dict(c) for c in candles],
                "volume_profile": [self._volume_to_dict(v) for v in volume_profile],
                "order_flow": order_flow,
                "market_depth": market_depth,
                "timestamp": time.time(),
                "market_status": "closed"
            }
            
        except Exception as e:
            logger.error(f"Error getting off-market data: {e}")
            return {"error": str(e)}
    
    def _simulate_market_depth(self, last_candle: Optional[HistoricalCandle]) -> Dict:
        """Simulate market depth from last candle"""
        if not last_candle:
            return {"bids": [], "asks": []}
        
        price = last_candle.close
        spread = price * 0.001  # 0.1% spread
        
        # Generate bid levels
        bids = []
        for i in range(20):
            bid_price = price - (spread * (i + 1))
            bid_qty = max(100, int(1000 / (i + 1)))
            bids.append([round(bid_price, 2), bid_qty])
        
        # Generate ask levels
        asks = []
        for i in range(20):
            ask_price = price + (spread * (i + 1))
            ask_qty = max(100, int(1000 / (i + 1)))
            asks.append([round(ask_price, 2), ask_qty])
        
        return {
            "bids": bids,
            "asks": asks,
            "last_trade": {
                "price": price,
                "quantity": last_candle.volume,
                "side": "buy" if last_candle.close > last_candle.open else "sell"
            }
        }
    
    def _candle_to_dict(self, candle: HistoricalCandle) -> Dict:
        """Convert candle to dictionary"""
        return {
            "timestamp": candle.timestamp,
            "open": candle.open,
            "high": candle.high,
            "low": candle.low,
            "close": candle.close,
            "volume": candle.volume,
            "ohlc": candle.ohlc
        }
    
    def _volume_to_dict(self, volume: VolumeProfile) -> Dict:
        """Convert volume profile to dictionary"""
        return {
            "price": volume.price,
            "volume": volume.volume,
            "buy_volume": volume.buy_volume,
            "sell_volume": volume.sell_volume,
            "timestamp": volume.timestamp
        }

# Global historical data manager
historical_manager = HistoricalDataManager()
