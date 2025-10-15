"""
DhanHQ Official SDK Integration
Provides WebSocket market data feeds using the official dhanhq Python package
"""

import asyncio
import json
import logging
import os
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime
from queue import Queue

from dhanhq import DhanContext, MarketFeed, FullDepth
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class DhanMarketFeed:
    """
    Manages real-time market data feeds using DhanHQ official SDK
    Handles both ticker data and full 20-level market depth
    """

    def __init__(self, client_id: str, access_token: str):
        self.client_id = client_id
        self.access_token = access_token
        self.dhan_context = DhanContext(client_id, access_token)

        self.ticker_feed = None
        self.depth_feed = None
        self.is_connected = False
        self.data_queue = Queue()

        self.on_ticker_callback: Optional[Callable] = None
        self.on_depth_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None

        self.current_instruments = []
        self.feed_thread = None
        self.stop_flag = threading.Event()

    def set_ticker_callback(self, callback: Callable):
        """Set callback for ticker updates"""
        self.on_ticker_callback = callback

    def set_depth_callback(self, callback: Callable):
        """Set callback for market depth updates"""
        self.on_depth_callback = callback

    def set_error_callback(self, callback: Callable):
        """Set callback for errors"""
        self.on_error_callback = callback

    def subscribe_ticker(self, exchange_segment: int, security_id: str):
        """
        Subscribe to ticker feed for a symbol

        Args:
            exchange_segment: 1 for NSE, 2 for BSE
            security_id: Security ID from Dhan
        """
        try:
            instruments = [
                (exchange_segment, security_id, MarketFeed.Ticker),
                (exchange_segment, security_id, MarketFeed.Quote)
            ]

            self.current_instruments = instruments
            self.ticker_feed = MarketFeed(self.dhan_context, instruments, "v2")

            logger.info(f"Subscribed to ticker feed: {security_id}")
            self.is_connected = True

            # Start feed in separate thread
            self._start_ticker_feed()

        except Exception as e:
            logger.error(f"Error subscribing to ticker: {e}")
            if self.on_error_callback:
                self.on_error_callback(str(e))

    def subscribe_market_depth(self, exchange_segment: int, security_id: str):
        """
        Subscribe to 20-level market depth

        Args:
            exchange_segment: 1 for NSE, 2 for BSE
            security_id: Security ID from Dhan
        """
        try:
            instruments = [(exchange_segment, security_id)]

            self.depth_feed = FullDepth(self.dhan_context, instruments)

            logger.info(f"Subscribed to market depth: {security_id}")
            self.is_connected = True

            # Start depth feed in separate thread
            self._start_depth_feed()

        except Exception as e:
            logger.error(f"Error subscribing to market depth: {e}")
            if self.on_error_callback:
                self.on_error_callback(str(e))

    def _start_ticker_feed(self):
        """Start ticker feed in background thread"""
        def run_ticker():
            try:
                while not self.stop_flag.is_set() and self.ticker_feed:
                    try:
                        self.ticker_feed.run_forever()
                        data = self.ticker_feed.get_data()

                        if data and self.on_ticker_callback:
                            self.on_ticker_callback(data)

                    except Exception as e:
                        logger.error(f"Error in ticker feed: {e}")
                        if self.on_error_callback:
                            self.on_error_callback(str(e))
                        break

            except Exception as e:
                logger.error(f"Ticker feed thread error: {e}")
                self.is_connected = False

        self.feed_thread = threading.Thread(target=run_ticker, daemon=True)
        self.feed_thread.start()

    def _start_depth_feed(self):
        """Start market depth feed in background thread"""
        def run_depth():
            try:
                while not self.stop_flag.is_set() and self.depth_feed:
                    try:
                        self.depth_feed.run_forever()
                        data = self.depth_feed.get_data()

                        if data and self.on_depth_callback:
                            self.on_depth_callback(data)

                    except Exception as e:
                        logger.error(f"Error in depth feed: {e}")
                        if self.on_error_callback:
                            self.on_error_callback(str(e))
                        break

            except Exception as e:
                logger.error(f"Depth feed thread error: {e}")
                self.is_connected = False

        self.feed_thread = threading.Thread(target=run_depth, daemon=True)
        self.feed_thread.start()

    def unsubscribe(self):
        """Stop all feeds and disconnect"""
        try:
            self.stop_flag.set()
            self.is_connected = False

            if self.ticker_feed:
                self.ticker_feed = None

            if self.depth_feed:
                self.depth_feed = None

            logger.info("Unsubscribed from all feeds")

        except Exception as e:
            logger.error(f"Error unsubscribing: {e}")

    def get_connection_status(self) -> Dict:
        """Get current connection status"""
        return {
            "connected": self.is_connected,
            "ticker_active": self.ticker_feed is not None,
            "depth_active": self.depth_feed is not None,
            "instruments": len(self.current_instruments)
        }


class DhanMarketDataManager:
    """
    High-level manager for DhanHQ market data
    Provides unified interface for order flow visualization
    """

    def __init__(self):
        self.client_id = os.getenv("DHAN_CLIENT_ID", "")
        self.access_token = os.getenv("DHAN_API_KEY", "")

        if not self.client_id or not self.access_token:
            raise ValueError("DHAN_CLIENT_ID and DHAN_API_KEY must be set in environment")

        self.market_feed = DhanMarketFeed(self.client_id, self.access_token)
        self.current_symbol = None
        self.current_security_id = None

        # Callbacks for data processing
        self.depth_update_callback = None
        self.ticker_update_callback = None
        self.trade_update_callback = None

    def subscribe_symbol(self, security_id: str, symbol: str, exchange_segment: int = 1):
        """
        Subscribe to market data for a symbol

        Args:
            security_id: Dhan security ID
            symbol: Symbol name (e.g., RELIANCE)
            exchange_segment: 1 for NSE, 2 for BSE
        """
        try:
            # Unsubscribe from previous symbol
            if self.current_security_id:
                self.market_feed.unsubscribe()

            self.current_symbol = symbol
            self.current_security_id = security_id

            # Set callbacks
            self.market_feed.set_depth_callback(self._handle_depth_update)
            self.market_feed.set_ticker_callback(self._handle_ticker_update)
            self.market_feed.set_error_callback(self._handle_error)

            # Subscribe to both depth and ticker
            self.market_feed.subscribe_market_depth(exchange_segment, security_id)
            self.market_feed.subscribe_ticker(exchange_segment, security_id)

            logger.info(f"Subscribed to {symbol} ({security_id})")

        except Exception as e:
            logger.error(f"Error subscribing to symbol: {e}")
            raise

    def _handle_depth_update(self, data: Dict):
        """Process market depth update from DhanHQ"""
        try:
            if not data:
                return

            # Transform DhanHQ depth data to our format
            transformed_data = self._transform_depth_data(data)

            if self.depth_update_callback:
                self.depth_update_callback(transformed_data)

        except Exception as e:
            logger.error(f"Error handling depth update: {e}")

    def _handle_ticker_update(self, data: Dict):
        """Process ticker update from DhanHQ"""
        try:
            if not data:
                return

            # Transform ticker data
            transformed_data = self._transform_ticker_data(data)

            if self.ticker_update_callback:
                self.ticker_update_callback(transformed_data)

            # Extract trade information if available
            if 'last_trade_price' in data and 'last_trade_qty' in data:
                trade_data = {
                    'price': data['last_trade_price'],
                    'quantity': data['last_trade_qty'],
                    'timestamp': data.get('timestamp', datetime.now().timestamp())
                }

                if self.trade_update_callback:
                    self.trade_update_callback(trade_data)

        except Exception as e:
            logger.error(f"Error handling ticker update: {e}")

    def _handle_error(self, error_message: str):
        """Handle errors from DhanHQ feed"""
        logger.error(f"DhanHQ feed error: {error_message}")

    def _transform_depth_data(self, data: Dict) -> Dict:
        """Transform DhanHQ market depth to our format"""
        try:
            # DhanHQ provides depth data with bid/ask arrays
            bids = data.get('depth', {}).get('buy', [])
            asks = data.get('depth', {}).get('sell', [])

            # Convert to [price, quantity] format
            formatted_bids = [[item.get('price', 0), item.get('quantity', 0)] for item in bids]
            formatted_asks = [[item.get('price', 0), item.get('quantity', 0)] for item in asks]

            return {
                'type': 'depth_update',
                'instrument_token': self.current_security_id,
                'symbol': self.current_symbol,
                'bids': formatted_bids,
                'asks': formatted_asks,
                'timestamp': datetime.now().timestamp()
            }

        except Exception as e:
            logger.error(f"Error transforming depth data: {e}")
            return {}

    def _transform_ticker_data(self, data: Dict) -> Dict:
        """Transform DhanHQ ticker to our format"""
        try:
            return {
                'type': 'quote_update',
                'instrument_token': self.current_security_id,
                'symbol': self.current_symbol,
                'ltp': data.get('last_price', 0),
                'change': data.get('change', 0),
                'change_percent': data.get('change_percent', 0),
                'volume': data.get('volume', 0),
                'timestamp': datetime.now().timestamp()
            }

        except Exception as e:
            logger.error(f"Error transforming ticker data: {e}")
            return {}

    def set_depth_callback(self, callback: Callable):
        """Set callback for depth updates"""
        self.depth_update_callback = callback

    def set_ticker_callback(self, callback: Callable):
        """Set callback for ticker updates"""
        self.ticker_update_callback = callback

    def set_trade_callback(self, callback: Callable):
        """Set callback for trade updates"""
        self.trade_update_callback = callback

    def unsubscribe(self):
        """Unsubscribe from all feeds"""
        self.market_feed.unsubscribe()
        self.current_symbol = None
        self.current_security_id = None

    def get_status(self) -> Dict:
        """Get current status"""
        return {
            'connected': self.market_feed.is_connected,
            'current_symbol': self.current_symbol,
            'security_id': self.current_security_id,
            'feed_status': self.market_feed.get_connection_status()
        }


# Global instance
dhan_manager = None

def get_dhan_manager() -> DhanMarketDataManager:
    """Get or create DhanHQ manager instance"""
    global dhan_manager
    if dhan_manager is None:
        dhan_manager = DhanMarketDataManager()
    return dhan_manager
