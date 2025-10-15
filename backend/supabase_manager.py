"""
Supabase Database Manager
Handles persistent storage for symbols, market data, and user preferences
"""

import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SupabaseManager:
    """Manages Supabase database operations"""

    def __init__(self):
        self.url = os.getenv("VITE_SUPABASE_URL")
        self.key = os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY")

        if not self.url or not self.key:
            logger.warning("Supabase credentials not found. Database features disabled.")
            self.client = None
            return

        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if Supabase is available"""
        return self.client is not None

    async def save_symbol(self, symbol_data: Dict) -> bool:
        """
        Save symbol information to database

        Args:
            symbol_data: Dictionary containing symbol, token, name, sector, etc.
        """
        if not self.client:
            return False

        try:
            data = {
                'symbol': symbol_data.get('symbol'),
                'token': symbol_data.get('token'),
                'name': symbol_data.get('name'),
                'sector': symbol_data.get('sector'),
                'market_cap': symbol_data.get('market_cap'),
                'last_updated': datetime.now().isoformat(),
                'is_active': True
            }

            result = self.client.table('symbols').upsert(data).execute()
            logger.info(f"Saved symbol {symbol_data.get('symbol')} to database")
            return True

        except Exception as e:
            logger.error(f"Error saving symbol: {e}")
            return False

    async def get_symbol(self, symbol: str) -> Optional[Dict]:
        """Get symbol information from database"""
        if not self.client:
            return None

        try:
            result = self.client.table('symbols')\
                .select('*')\
                .eq('symbol', symbol)\
                .eq('is_active', True)\
                .maybeSingle()\
                .execute()

            if result.data:
                return result.data

            return None

        except Exception as e:
            logger.error(f"Error getting symbol: {e}")
            return None

    async def search_symbols(self, query: str, limit: int = 20) -> List[Dict]:
        """Search symbols in database"""
        if not self.client:
            return []

        try:
            # Search by symbol or name
            result = self.client.table('symbols')\
                .select('*')\
                .eq('is_active', True)\
                .or_(f'symbol.ilike.%{query}%,name.ilike.%{query}%')\
                .limit(limit)\
                .execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return []

    async def get_popular_symbols(self, limit: int = 50) -> List[Dict]:
        """Get most popular symbols"""
        if not self.client:
            return []

        try:
            result = self.client.table('symbols')\
                .select('*')\
                .eq('is_active', True)\
                .order('last_updated', desc=True)\
                .limit(limit)\
                .execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error getting popular symbols: {e}")
            return []

    async def save_market_data(self, market_data: Dict) -> bool:
        """Save market data snapshot"""
        if not self.client:
            return False

        try:
            data = {
                'symbol': market_data.get('symbol'),
                'timestamp': market_data.get('timestamp'),
                'ltp': market_data.get('ltp'),
                'volume': market_data.get('volume'),
                'bid_price': market_data.get('bid_price'),
                'ask_price': market_data.get('ask_price'),
                'data': market_data
            }

            result = self.client.table('market_data').insert(data).execute()
            return True

        except Exception as e:
            logger.error(f"Error saving market data: {e}")
            return False

    async def save_user_preference(self, user_id: str, key: str, value: any) -> bool:
        """Save user preference"""
        if not self.client:
            return False

        try:
            data = {
                'user_id': user_id,
                'key': key,
                'value': value,
                'updated_at': datetime.now().isoformat()
            }

            result = self.client.table('user_preferences').upsert(data).execute()
            return True

        except Exception as e:
            logger.error(f"Error saving user preference: {e}")
            return False

    async def get_user_preference(self, user_id: str, key: str) -> Optional[any]:
        """Get user preference"""
        if not self.client:
            return None

        try:
            result = self.client.table('user_preferences')\
                .select('value')\
                .eq('user_id', user_id)\
                .eq('key', key)\
                .maybeSingle()\
                .execute()

            if result.data:
                return result.data.get('value')

            return None

        except Exception as e:
            logger.error(f"Error getting user preference: {e}")
            return None

    async def cleanup_old_data(self, days: int = 7) -> bool:
        """Cleanup old market data"""
        if not self.client:
            return False

        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            result = self.client.table('market_data')\
                .delete()\
                .lt('timestamp', cutoff_date)\
                .execute()

            logger.info(f"Cleaned up market data older than {days} days")
            return True

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False


# Global instance
supabase_manager = None

def get_supabase_manager() -> SupabaseManager:
    """Get or create Supabase manager instance"""
    global supabase_manager
    if supabase_manager is None:
        supabase_manager = SupabaseManager()
    return supabase_manager
