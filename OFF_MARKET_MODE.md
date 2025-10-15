# Off-Market Mode Documentation

## 🕐 **Off-Market Hours Visualization**

When the market is closed, the Order Flow Visualizer automatically switches to **Off-Market Mode**, providing comprehensive historical data analysis with advanced visualization features.

## 🎯 **Key Features**

### **📊 Historical Data Visualization**
- **Candle Charts**: Interactive OHLC charts with multiple timeframes
- **Volume Profile**: Buy/sell volume analysis at different price levels
- **Order Flow Simulation**: Reconstructed tick-by-tick data from historical candles
- **Market Depth Simulation**: Simulated order book based on last known prices

### **⏰ Timeframe Options**
- **1 Minute**: High-resolution intraday analysis
- **5 Minutes**: Short-term trend analysis
- **15 Minutes**: Medium-term patterns
- **1 Hour**: Daily session analysis
- **1 Day**: Long-term trend analysis

### **📈 Advanced Analytics**
- **Volume Bubbles**: Visual representation of trading volume intensity
- **Order Flow Candles**: Reconstructed order flow from historical data
- **Price Action Analysis**: Support/resistance level identification
- **Volume Profile**: Price levels with highest trading activity

## 🏗️ **Technical Implementation**

### **Backend Components**

#### **1. Historical Data Manager**
```python
# backend/historical_data_manager.py
class HistoricalDataManager:
    async def get_historical_data(symbol, timeframe, days)
    async def generate_volume_profile(candles)
    async def simulate_order_flow(candles)
    def is_market_hours()
```

#### **2. API Endpoints**
```python
# Market status check
GET /market/status

# Historical data retrieval
GET /historical/{symbol}?timeframe=1min&days=1

# Off-market visualization
GET /off-market/{symbol}?timeframe=1min
```

#### **3. WebSocket Integration**
```javascript
// Automatic market status detection
{
  "type": "market_status",
  "is_market_hours": false,
  "market_status": "closed"
}

// Historical data streaming
{
  "type": "off_market_data",
  "symbol": "RELIANCE",
  "timeframe": "1min",
  "candles": [...],
  "volume_profile": [...],
  "order_flow": [...],
  "market_depth": {...}
}
```

### **Frontend Components**

#### **1. OffMarketVisualizer Component**
```typescript
// frontend/src/components/OffMarketVisualizer.tsx
interface OffMarketData {
  type: string;
  symbol: string;
  timeframe: string;
  candles: HistoricalCandle[];
  volume_profile: VolumeProfile[];
  order_flow: any[];
  market_depth: MarketDepth;
  timestamp: number;
  market_status: string;
}
```

#### **2. Chart Rendering**
- **D3.js Integration**: Interactive candle charts
- **Volume Profile Charts**: Buy/sell volume visualization
- **Order Flow Display**: Simulated tick data
- **Market Depth Table**: Simulated order book

## 📊 **Data Structures**

### **Historical Candle**
```typescript
interface HistoricalCandle {
  timestamp: number;        // Unix timestamp
  open: number;            // Opening price
  high: number;           // Highest price
  low: number;            // Lowest price
  close: number;          // Closing price
  volume: number;         // Trading volume
  ohlc: number[];         // [open, high, low, close]
}
```

### **Volume Profile**
```typescript
interface VolumeProfile {
  price: number;          // Price level
  volume: number;         // Total volume
  buy_volume: number;     // Buy volume
  sell_volume: number;    // Sell volume
  timestamp: number;       // Timestamp
}
```

### **Simulated Order Flow**
```typescript
interface OrderFlowTick {
  type: "tick";
  price: number;
  quantity: number;
  side: "buy" | "sell";
  timestamp: number;
}
```

## 🔄 **Market Status Detection**

### **NSE Market Hours**
- **Trading Hours**: 9:15 AM - 3:30 PM (Monday to Friday)
- **Pre-Market**: 9:00 AM - 9:15 AM
- **Post-Market**: 3:40 PM - 4:00 PM
- **Weekends**: Market closed

### **Automatic Switching**
```python
def is_market_hours() -> bool:
    now = datetime.now()
    current_time = now.time()
    
    # NSE market hours: 9:15 AM - 3:30 PM
    market_start = datetime.strptime("09:15", "%H:%M").time()
    market_end = datetime.strptime("15:30", "%H:%M").time()
    
    # Check if it's a weekday
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
        
    return market_start <= current_time <= market_end
```

## 📈 **Visualization Features**

### **1. Interactive Candle Charts**
- **OHLC Visualization**: Standard candlestick charts
- **Volume Overlay**: Volume bars below price chart
- **Time Navigation**: Zoom and pan functionality
- **Price Levels**: Support/resistance highlighting

### **2. Volume Profile Analysis**
- **Price-Volume Relationship**: Volume at each price level
- **Buy/Sell Pressure**: Color-coded volume analysis
- **Volume Clusters**: High-volume price areas
- **POC (Point of Control)**: Price with highest volume

### **3. Order Flow Simulation**
- **Tick Reconstruction**: Simulated tick-by-tick data
- **Buy/Sell Imbalance**: Order flow direction analysis
- **Volume Bubbles**: Visual volume intensity
- **Time & Sales**: Reconstructed trade tape

### **4. Market Depth Simulation**
- **Bid/Ask Levels**: Simulated order book
- **Spread Analysis**: Bid-ask spread visualization
- **Depth Visualization**: Order book depth
- **Last Trade Info**: Simulated last trade data

## 🎛️ **User Controls**

### **Timeframe Selection**
```typescript
const timeframes = [
  { value: '1min', label: '1 Min', description: '1 minute candles' },
  { value: '5min', label: '5 Min', description: '5 minute candles' },
  { value: '15min', label: '15 Min', description: '15 minute candles' },
  { value: '1hour', label: '1 Hour', description: '1 hour candles' },
  { value: '1day', label: '1 Day', description: 'Daily candles' }
];
```

### **Visualization Options**
- **Volume Profile Toggle**: Show/hide volume profile
- **Order Flow Toggle**: Show/hide order flow simulation
- **Chart Type Selection**: Candlestick, line, or bar charts
- **Time Range Selection**: Custom date range selection

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Historical data settings
HISTORICAL_CACHE_DURATION=3600  # 1 hour cache
MAX_HISTORICAL_DAYS=365         # Maximum days to fetch
DEFAULT_TIMEFRAME=1min          # Default timeframe
```

### **API Configuration**
```python
# DhanHQ Historical Data API
DHAN_HISTORICAL_URL = "https://api.dhan.co/v2/historical"
DHAN_QUOTE_URL = "https://api.dhan.co/v2/market/quote"

# Cache settings
CACHE_DURATION = 3600  # 1 hour
MAX_CACHE_SIZE = 1000  # Maximum cached symbols
```

## 📊 **Performance Optimization**

### **Data Caching**
- **SQLite Database**: Persistent symbol cache
- **Memory Cache**: In-memory data caching
- **API Rate Limiting**: Respect DhanHQ API limits
- **Data Compression**: Efficient data storage

### **Rendering Optimization**
- **D3.js Performance**: Efficient chart rendering
- **Data Pagination**: Large dataset handling
- **Lazy Loading**: On-demand data loading
- **Memory Management**: Efficient memory usage

## 🚀 **Usage Examples**

### **1. Basic Off-Market Visualization**
```typescript
// Automatic market status detection
if (!isMarketHours) {
  // Switch to off-market mode
  setOffMarketData(historicalData);
}
```

### **2. Timeframe Change**
```typescript
const handleTimeframeChange = (timeframe: string) => {
  // Request new historical data
  socket.send(JSON.stringify({
    type: 'change_timeframe',
    timeframe
  }));
};
```

### **3. Symbol Change**
```typescript
const handleSymbolChange = (symbol: string) => {
  // Fetch historical data for new symbol
  const historicalData = await fetchHistoricalData(symbol, timeframe);
  setOffMarketData(historicalData);
};
```

## 🎯 **Benefits**

### **For Traders**
- **24/7 Analysis**: Analyze markets even when closed
- **Historical Patterns**: Study past market behavior
- **Strategy Testing**: Test trading strategies on historical data
- **Education**: Learn market dynamics without live pressure

### **For Developers**
- **Data Analysis**: Comprehensive historical data access
- **Backtesting**: Test algorithms on historical data
- **Research**: Market behavior analysis
- **Learning**: Understanding order flow dynamics

## 🔮 **Future Enhancements**

### **Planned Features**
- **Backtesting Engine**: Strategy backtesting capabilities
- **Pattern Recognition**: Automated pattern detection
- **Alert System**: Historical data alerts
- **Export Functionality**: Data export capabilities
- **Advanced Analytics**: More sophisticated analysis tools

### **Integration Possibilities**
- **Machine Learning**: AI-powered analysis
- **Sentiment Analysis**: News sentiment integration
- **Economic Indicators**: Macro data integration
- **Cross-Asset Analysis**: Multi-asset correlation

## 📚 **API Reference**

### **Historical Data Endpoints**
```bash
# Get market status
GET /market/status

# Get historical data
GET /historical/{symbol}?timeframe=1min&days=1

# Get off-market visualization
GET /off-market/{symbol}?timeframe=1min
```

### **WebSocket Messages**
```javascript
// Market status
{
  "type": "market_status",
  "is_market_hours": false,
  "market_status": "closed"
}

// Historical data
{
  "type": "off_market_data",
  "symbol": "RELIANCE",
  "timeframe": "1min",
  "candles": [...],
  "volume_profile": [...],
  "order_flow": [...],
  "market_depth": {...}
}
```

The Off-Market Mode provides a comprehensive solution for historical data analysis, ensuring traders can continue their market research and strategy development even when markets are closed! 🚀
