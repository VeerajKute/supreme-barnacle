# DhanHQ Official SDK Integration Guide

## 🎯 What Changed

The Order Flow Visualizer now uses the **official dhanhq Python SDK** instead of raw WebSocket connections. This provides:

- ✅ **More reliable** market data streaming
- ✅ **Better error handling** and reconnection logic
- ✅ **Official support** from DhanHQ
- ✅ **Easier maintenance** with SDK updates
- ✅ **20-level market depth** support
- ✅ **Persistent storage** with Supabase database

## 📦 New Dependencies

### Python Backend
```bash
pip install dhanhq==2.1.0
pip install supabase==2.3.0
```

All dependencies are now in `requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pydantic==2.5.0
aiofiles==23.2.1
python-dotenv==1.0.0
aiohttp==3.9.1
dhanhq==2.1.0
supabase==2.3.0
```

## 🔧 New Architecture

### Backend Modules

1. **`dhan_integration.py`** - Official DhanHQ SDK wrapper
   - `DhanMarketFeed` - Manages WebSocket market feeds
   - `DhanMarketDataManager` - High-level interface for order flow
   - Handles both ticker and 20-level depth feeds

2. **`supabase_manager.py`** - Database persistence layer
   - Symbol caching in Supabase
   - Market data storage
   - User preferences
   - Search functionality

3. **`main_v2.py`** - Updated FastAPI server
   - Uses official DhanHQ SDK
   - Integrates with Supabase
   - Maintains backward compatibility

4. **`symbol_manager.py`** - Enhanced with Supabase
   - Falls back to database for symbol lookups
   - Improved caching strategy

5. **`historical_data_manager.py`** - Unchanged
   - Still provides off-market visualization

### Database Schema (Supabase)

Tables created:
- **`symbols`** - Stock symbols with metadata
- **`market_data`** - Historical market data snapshots
- **`user_preferences`** - User settings
- **`symbol_requests`** - Symbol discovery requests

## 🚀 Setup Instructions

### 1. Get DhanHQ Credentials

1. Login to [web.dhan.co](https://web.dhan.co/)
2. Go to **My Profile** → **Access DhanHQ APIs**
3. Generate **Access Token** (valid for 24 hours)
4. Note your **Client ID**

### 2. Configure Environment Variables

Update your `.env` file:

```bash
# DhanHQ Credentials
DHAN_CLIENT_ID=your_client_id_here
DHAN_API_KEY=your_access_token_here

# Supabase (Already configured by Bolt.new)
VITE_SUPABASE_URL=https://0ec90b57d6e95fcbda19832f.supabase.co
VITE_SUPABASE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install individually
pip install dhanhq==2.1.0
pip install supabase==2.3.0
```

### 4. Initialize Database

The database tables are automatically created when you run the migration. They include:

- Pre-populated with top 10 NSE stocks
- Indexes for fast search
- RLS policies for security

### 5. Start the Application

**Option A: Use new main_v2.py**
```bash
# Backend
python backend/main_v2.py

# Frontend (in separate terminal)
cd frontend
npm install
npm start
```

**Option B: Replace old main.py (Recommended)**
```bash
# Backup old main.py
mv backend/main.py backend/main_old.py

# Use new version
mv backend/main_v2.py backend/main.py

# Start normally
python start_backend.py
```

## 📊 How It Works

### Market Data Flow

```
DhanHQ SDK → dhan_integration.py → main_v2.py →
WebSocket → Frontend → Visualization
         ↓
    Supabase DB (Persistent Storage)
```

### Symbol Discovery Flow

```
User Search →
  1. Check Supabase Database
  2. Check Local Cache
  3. Fetch from DhanHQ/NSE APIs
  4. Cache in Supabase + Local
  5. Return to User
```

## 🔌 API Usage Examples

### Using DhanHQ Integration

```python
from dhan_integration import get_dhan_manager

# Initialize
dhan_manager = get_dhan_manager()

# Set callbacks
dhan_manager.set_depth_callback(handle_depth)
dhan_manager.set_ticker_callback(handle_ticker)
dhan_manager.set_trade_callback(handle_trade)

# Subscribe to symbol
dhan_manager.subscribe_symbol(
    security_id="2885633",
    symbol="RELIANCE",
    exchange_segment=1  # 1=NSE, 2=BSE
)

# Get status
status = dhan_manager.get_status()
print(status)
```

### Using Supabase Manager

```python
from supabase_manager import get_supabase_manager

# Initialize
db = get_supabase_manager()

# Save symbol
await db.save_symbol({
    'symbol': 'RELIANCE',
    'token': '2885633',
    'name': 'Reliance Industries Ltd',
    'sector': 'Energy'
})

# Search symbols
results = await db.search_symbols('HDFC', limit=10)

# Get popular symbols
popular = await db.get_popular_symbols(50)
```

## 🎯 Key Features

### 1. Official DhanHQ SDK
- **MarketFeed** - Real-time ticker and quotes
- **FullDepth** - 20-level market depth
- **Automatic reconnection** - Built-in retry logic
- **Error handling** - Proper exception management

### 2. Supabase Integration
- **Persistent symbols** - No loss of discovered symbols
- **Fast search** - Database-backed symbol search
- **Analytics** - Track symbol popularity
- **User preferences** - Store user settings

### 3. Backward Compatibility
- **Fallback to cache** - Works without database
- **Same API endpoints** - Frontend unchanged
- **Graceful degradation** - Features work independently

## 🐛 Troubleshooting

### DhanHQ Connection Issues

```python
# Check status
dhan_manager = get_dhan_manager()
status = dhan_manager.get_status()

# Expected output:
{
    'connected': True,
    'current_symbol': 'RELIANCE',
    'security_id': '2885633',
    'feed_status': {
        'ticker_active': True,
        'depth_active': True
    }
}
```

### Supabase Connection Issues

```python
# Check availability
db = get_supabase_manager()
if db.is_available():
    print("Supabase connected")
else:
    print("Using local cache only")
```

### Common Errors

**Error: "DHAN_CLIENT_ID and DHAN_API_KEY must be set"**
- Solution: Add credentials to `.env` file

**Error: "Supabase credentials not found"**
- Solution: Check `VITE_SUPABASE_URL` and `VITE_SUPABASE_SUPABASE_ANON_KEY` in `.env`

**Error: "dhanhq module not found"**
- Solution: Run `pip install dhanhq==2.1.0`

## 📈 Performance Improvements

### Before (Raw WebSocket)
- Manual connection management
- Complex error handling
- No persistent storage
- Limited symbol discovery

### After (Official SDK + Supabase)
- ✅ Automatic reconnection
- ✅ Built-in error handling
- ✅ Persistent symbol cache
- ✅ Database-backed search
- ✅ 20-level market depth support
- ✅ Better reliability

## 🔮 Future Enhancements

- [ ] Real-time order updates using `OrderUpdate` class
- [ ] Historical data storage in Supabase
- [ ] Advanced analytics on market data
- [ ] User authentication and personalization
- [ ] Multi-symbol watchlists
- [ ] Price alerts and notifications

## 📚 Resources

- [DhanHQ Python SDK](https://github.com/dhan-oss/DhanHQ-py)
- [DhanHQ API Documentation](https://dhanhq.co/docs/v2/)
- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## ✅ Migration Checklist

- [x] Install dhanhq SDK
- [x] Install supabase SDK
- [x] Create dhan_integration.py
- [x] Create supabase_manager.py
- [x] Create main_v2.py
- [x] Set up Supabase database
- [x] Migrate database schema
- [x] Pre-populate symbols
- [x] Update documentation

## 🎉 Result

Your Order Flow Visualizer now has:
- **Enterprise-grade** market data integration
- **Persistent** symbol storage
- **Scalable** architecture
- **Production-ready** error handling
- **Official support** from DhanHQ

Ready to visualize order flow like never before! 🚀
