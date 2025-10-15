"""
Dynamic Symbol Manager for NSE stocks
Automatically discovers and manages stock symbols without manual updates
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import aiohttp
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class SymbolManager:
    """Manages dynamic symbol discovery and caching"""
    
    def __init__(self, db_path: str = "data/symbols.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.symbols_cache: Dict[str, Dict] = {}
        self.last_update = 0
        self.update_interval = 3600  # 1 hour
        self.cache_duration = 86400  # 24 hours
        
        # Initialize database
        self._init_database()
        
        # Load cached symbols
        self._load_cached_symbols()
    
    def _init_database(self):
        """Initialize SQLite database for symbol storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS symbols (
                    symbol TEXT PRIMARY KEY,
                    token TEXT NOT NULL,
                    name TEXT NOT NULL,
                    sector TEXT,
                    market_cap TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS symbol_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            conn.commit()
    
    def _load_cached_symbols(self):
        """Load symbols from database cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT symbol, token, name, sector, market_cap 
                    FROM symbols 
                    WHERE is_active = 1 
                    ORDER BY last_updated DESC
                """)
                
                for row in cursor.fetchall():
                    symbol, token, name, sector, market_cap = row
                    self.symbols_cache[symbol] = {
                        'token': token,
                        'name': name,
                        'sector': sector,
                        'market_cap': market_cap
                    }
                
                logger.info(f"Loaded {len(self.symbols_cache)} cached symbols")
                
        except Exception as e:
            logger.error(f"Error loading cached symbols: {e}")
    
    async def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information, fetch if not cached"""
        symbol = symbol.upper()
        
        # Check cache first
        if symbol in self.symbols_cache:
            return self.symbols_cache[symbol]
        
        # Try to fetch from DhanHQ API
        symbol_info = await self._fetch_symbol_from_api(symbol)
        if symbol_info:
            self._cache_symbol(symbol, symbol_info)
            return symbol_info
        
        # Try alternative sources
        symbol_info = await self._fetch_symbol_alternative(symbol)
        if symbol_info:
            self._cache_symbol(symbol, symbol_info)
            return symbol_info
        
        # Log unknown symbol for manual review
        self._log_unknown_symbol(symbol)
        return None
    
    async def _fetch_symbol_from_api(self, symbol: str) -> Optional[Dict]:
        """Fetch symbol info from DhanHQ API"""
        try:
            # This would use DhanHQ's symbol search API
            # For now, we'll implement a mock that could be replaced with real API calls
            return await self._mock_symbol_fetch(symbol)
        except Exception as e:
            logger.error(f"Error fetching symbol {symbol} from API: {e}")
            return None
    
    async def _mock_symbol_fetch(self, symbol: str) -> Optional[Dict]:
        """Mock symbol fetch - replace with real DhanHQ API call"""
        # This is a placeholder - in real implementation, you would:
        # 1. Call DhanHQ's symbol search API
        # 2. Parse the response
        # 3. Extract token and company name
        
        # For demonstration, we'll return a mock response
        mock_symbols = {
            'AAPL': {'token': '1234567', 'name': 'APPLE INC', 'sector': 'Technology'},
            'GOOGL': {'token': '2345678', 'name': 'ALPHABET INC', 'sector': 'Technology'},
            'MSFT': {'token': '3456789', 'name': 'MICROSOFT CORP', 'sector': 'Technology'},
        }
        
        if symbol in mock_symbols:
            return mock_symbols[symbol]
        
        return None
    
    async def _fetch_symbol_alternative(self, symbol: str) -> Optional[Dict]:
        """Fetch symbol from alternative sources"""
        try:
            # Try DhanHQ API first, then NSE as fallback
            dhanhq_result = await self._fetch_from_dhanhq_api(symbol)
            if dhanhq_result:
                return dhanhq_result
            
            # Fallback to NSE API
            return await self._fetch_from_nse_api(symbol)
        except Exception as e:
            logger.error(f"Error fetching symbol {symbol} from alternative source: {e}")
            return None
    
    async def _fetch_from_dhanhq_api(self, symbol: str) -> Optional[Dict]:
        """Fetch symbol from DhanHQ API"""
        try:
            # DhanHQ market quote API
            url = "https://api.dhan.co/v2/market/quote"
            headers = {
                "access-token": os.getenv("DHAN_API_KEY", ""),
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            params = {
                "symbol": symbol,
                "segment": "NSE_EQ"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse DhanHQ response
                        if 'data' in data and data['data']:
                            quote_data = data['data'][0]
                            return {
                                'token': quote_data.get('instrument_token', ''),
                                'name': quote_data.get('companyName', symbol),
                                'sector': quote_data.get('industry', ''),
                                'market_cap': quote_data.get('marketCap', '')
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching from DhanHQ API: {e}")
            return None
    
    async def _fetch_from_nse_api(self, symbol: str) -> Optional[Dict]:
        """Fetch symbol from NSE API (fallback)"""
        try:
            # NSE API endpoint for symbol search
            url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse NSE response
                        if 'info' in data:
                            info = data['info']
                            return {
                                'token': info.get('token', ''),
                                'name': info.get('companyName', symbol),
                                'sector': info.get('industry', ''),
                                'market_cap': info.get('marketCap', '')
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching from NSE API: {e}")
            return None
    
    def _cache_symbol(self, symbol: str, info: Dict):
        """Cache symbol information"""
        self.symbols_cache[symbol] = info
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO symbols 
                    (symbol, token, name, sector, market_cap, last_updated, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    info.get('token', ''),
                    info.get('name', symbol),
                    info.get('sector', ''),
                    info.get('market_cap', ''),
                    datetime.now(),
                    1
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error caching symbol {symbol}: {e}")
    
    def _log_unknown_symbol(self, symbol: str):
        """Log unknown symbol for manual review"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO symbol_requests (symbol, status)
                    VALUES (?, ?)
                """, (symbol, 'unknown'))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging unknown symbol {symbol}: {e}")
    
    async def search_symbols(self, query: str, limit: int = 20) -> List[Dict]:
        """Search symbols by name or symbol"""
        query = query.upper()
        results = []
        
        # Search in cache
        for symbol, info in self.symbols_cache.items():
            if (query in symbol or 
                query in info.get('name', '').upper() or
                query in info.get('sector', '').upper()):
                results.append({
                    'symbol': symbol,
                    'token': info.get('token', ''),
                    'name': info.get('name', ''),
                    'sector': info.get('sector', ''),
                    'market_cap': info.get('market_cap', '')
                })
        
        # Sort by relevance (exact match first, then partial)
        results.sort(key=lambda x: (
            0 if query == x['symbol'] else
            1 if query in x['symbol'] else
            2 if query in x['name'].upper() else 3
        ))
        
        return results[:limit]
    
    async def get_popular_symbols(self, limit: int = 50) -> List[Dict]:
        """Get most popular/traded symbols"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT symbol, token, name, sector, market_cap
                    FROM symbols 
                    WHERE is_active = 1 
                    ORDER BY last_updated DESC
                    LIMIT ?
                """, (limit,))
                
                results = []
                for row in cursor.fetchall():
                    symbol, token, name, sector, market_cap = row
                    results.append({
                        'symbol': symbol,
                        'token': token,
                        'name': name,
                        'sector': sector,
                        'market_cap': market_cap
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Error getting popular symbols: {e}")
            return []
    
    async def update_symbol_cache(self):
        """Update symbol cache from external sources"""
        if time.time() - self.last_update < self.update_interval:
            return
        
        try:
            # Update from NSE API or other sources
            await self._update_from_nse()
            self.last_update = time.time()
            
        except Exception as e:
            logger.error(f"Error updating symbol cache: {e}")
    
    async def _update_from_nse(self):
        """Update symbols from NSE API"""
        try:
            # This would fetch the latest symbol list from NSE
            # For now, we'll implement a mock update
            logger.info("Updating symbol cache from NSE...")
            
            # In real implementation, you would:
            # 1. Fetch NIFTY 50, NIFTY 100, NIFTY 500 lists
            # 2. Update database with latest symbols
            # 3. Remove delisted symbols
            
        except Exception as e:
            logger.error(f"Error updating from NSE: {e}")
    
    def get_cached_symbols(self) -> Dict[str, Dict]:
        """Get all cached symbols"""
        return self.symbols_cache.copy()
    
    def get_symbol_count(self) -> int:
        """Get total number of cached symbols"""
        return len(self.symbols_cache)
    
    async def cleanup_old_symbols(self):
        """Remove old/inactive symbols"""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE symbols 
                    SET is_active = 0 
                    WHERE last_updated < ?
                """, (cutoff_date,))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error cleaning up old symbols: {e}")

# Global symbol manager instance
symbol_manager = SymbolManager()
