// Market data types
export interface MarketData {
  type: string;
  instrument_token: string;
  bids: [number, number][]; // [price, quantity]
  asks: [number, number][];
  last_trade?: {
    price: number;
    quantity: number;
    side: string;
  };
  timestamp: number;
}

export interface TradeData {
  price: number;
  quantity: number;
  side: 'buy' | 'sell';
  timestamp: number;
  tradeCount?: number;
}

export interface OrderBookLevel {
  price: number;
  quantity: number;
  total: number;
}

export interface AggregatedTrade {
  price: number;
  total_volume: number;
  buy_volume: number;
  sell_volume: number;
  trade_count: number;
  timestamp: number;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'depth_update' | 'aggregated_trades' | 'symbol_changed' | 'change_symbol';
  data?: any;
  timestamp?: number;
  symbol?: string;
}

// Component props types
export interface HeatmapCanvasProps {
  marketData: MarketData | null;
  trades: TradeData[];
  isPaused: boolean;
}

export interface OrderBookTableProps {
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
  isPaused: boolean;
}

export interface TradeTapeProps {
  trades: TradeData[];
  isPaused: boolean;
}

export interface SettingsPanelProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
  isPaused: boolean;
  onPauseToggle: () => void;
}

export interface StatusBarProps {
  isConnected: boolean;
  latency: number;
  messageCount: number;
  selectedSymbol: string;
}

// NSE Symbols configuration
export interface SymbolInfo {
  token: string;
  name: string;
}

// Default symbols for initial setup (replaced by dynamic system)
export const DEFAULT_SYMBOLS: Record<string, SymbolInfo> = {
  'RELIANCE': { token: '2885633', name: 'RELIANCE' },
  'TCS': { token: '2953217', name: 'TCS' },
  'HDFCBANK': { token: '341249', name: 'HDFC BANK' },
  'INFY': { token: '408065', name: 'INFOSYS' },
  'ITC': { token: '424961', name: 'ITC' },
  'BHARTIARTL': { token: '2714625', name: 'BHARTI AIRTEL' },
  'SBIN': { token: '779521', name: 'STATE BANK OF INDIA' },
  'ASIANPAINT': { token: '60417', name: 'ASIAN PAINTS' },
  'KOTAKBANK': { token: '492033', name: 'KOTAK MAHINDRA BANK' },
  'MARUTI': { token: '2815745', name: 'MARUTI SUZUKI' },
};

// Note: The system now uses dynamic symbol discovery
// All symbols are fetched from NSE APIs and cached automatically
// No need to maintain static lists anymore!

// Heatmap visualization types
export interface HeatmapPoint {
  price: number;
  volume: number;
  side: 'buy' | 'sell';
  timestamp: number;
  intensity: number;
}

export interface HeatmapConfig {
  width: number;
  height: number;
  priceRange: {
    min: number;
    max: number;
  };
  timeRange: number; // milliseconds
  colorScheme: 'blue-red' | 'green-red' | 'purple-orange';
  bubbleSize: 'small' | 'medium' | 'large';
}
