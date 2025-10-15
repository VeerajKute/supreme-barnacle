## 🚀 Quick Start Guide - Order Flow Visualizer v2

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- DhanHQ account with API access

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install fastapi uvicorn websockets pydantic aiofiles python-dotenv aiohttp dhanhq supabase
```

### Step 2: Configure DhanHQ Credentials

1. Login to [web.dhan.co](https://web.dhan.co/)
2. Navigate to: **My Profile** → **Access DhanHQ APIs**
3. Generate your **Access Token** (valid for 24 hours)
4. Note your **Client ID**

### Step 3: Update .env File

Create or update `.env` in the project root:

```bash
# DhanHQ Credentials (REQUIRED)
DHAN_CLIENT_ID=your_client_id_here
DHAN_API_KEY=your_access_token_here

# Supabase (Already configured)
VITE_SUPABASE_URL=https://0ec90b57d6e95fcbda19832f.supabase.co
VITE_SUPABASE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 4: Start Backend

**Option A: Use new v2 backend (Recommended)**
```bash
python3 start_backend_v2.py
```

**Option B: Replace old main.py**
```bash
cd backend
mv main.py main_old.py
mv main_v2.py main.py
cd ..
python3 start_backend.py
```

### Step 5: Start Frontend

```bash
cd frontend
npm install
npm start
```

### Step 6: Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

## ✅ Verify Installation

### Test Integration
```bash
python3 test_integration.py
```

Expected output:
```
Testing imports...
✓ dhanhq module imported
✓ supabase module imported
✓ dhan_integration module imported
✓ supabase_manager module imported

Testing Supabase connection...
✓ Supabase connected - Found 10 symbols

Testing symbol manager...
✓ Symbol manager working

Testing historical data manager...
✓ Historical manager working
  Market status: CLOSED

Testing DhanHQ manager...
✓ DhanHQ manager initialized

✓ All tests passed!
```

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'dhanhq'"
**Solution**: Install dependencies
```bash
pip install dhanhq==2.1.0
```

### Issue: "DHAN_CLIENT_ID and DHAN_API_KEY must be set"
**Solution**: Update .env file with your DhanHQ credentials

### Issue: "Supabase not available"
**Solution**: This is OK - the app will work with local cache. Supabase provides extra features like persistent storage.

### Issue: "Connection refused on port 8000"
**Solution**: Make sure backend is running
```bash
python3 start_backend_v2.py
```

### Issue: "Frontend won't connect to WebSocket"
**Solution**:
1. Ensure backend is running on port 8000
2. Check CORS settings in main_v2.py
3. Verify WebSocket URL in frontend (ws://localhost:8000/ws)

## 📊 What's New in v2

### Official DhanHQ SDK Integration
- ✅ MarketFeed - Real-time ticker and quotes
- ✅ FullDepth - 20-level market depth
- ✅ Automatic reconnection logic
- ✅ Better error handling

### Supabase Database
- ✅ Persistent symbol cache
- ✅ Fast database search
- ✅ Market data storage
- ✅ User preferences

### Architecture Improvements
- ✅ Modular design
- ✅ Better separation of concerns
- ✅ Easier to maintain
- ✅ Production-ready

## 📚 File Structure

```
project/
├── backend/
│   ├── main_v2.py              # New FastAPI server (use this!)
│   ├── dhan_integration.py     # DhanHQ SDK wrapper
│   ├── supabase_manager.py     # Database layer
│   ├── symbol_manager.py       # Symbol discovery
│   └── historical_data_manager.py  # Off-market data
│
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/              # Custom hooks
│   │   └── types/              # TypeScript types
│   └── package.json
│
├── requirements.txt            # Python dependencies
├── start_backend_v2.py         # Backend startup script
├── test_integration.py         # Integration tests
├── INTEGRATION_GUIDE.md        # Detailed integration docs
├── QUICKSTART.md               # This file
└── .env                        # Environment variables
```

## 🎯 Next Steps

1. **Customize Symbols**: Add your favorite stocks to the database
2. **Set Preferences**: Configure color schemes and layouts
3. **Explore Features**: Try different timeframes and visualization options
4. **Monitor Performance**: Check latency and connection status
5. **Provide Feedback**: Report issues or suggest improvements

## 💡 Pro Tips

### Refresh DhanHQ Token Daily
DhanHQ access tokens expire after 24 hours. Update your `.env` file daily with a fresh token.

### Use Database for Better Performance
Supabase provides faster symbol search and persistent caching. The 10 default symbols are pre-populated!

### Check Market Hours
The app automatically detects market hours (9:15 AM - 3:30 PM IST) and switches to historical mode when closed.

### Monitor Connection Status
Watch the status bar for connection health, latency, and message count.

## 🆘 Need Help?

- Check the [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed documentation
- Review [DhanHQ API Docs](https://dhanhq.co/docs/v2/)
- Check console logs for errors
- Verify environment variables
- Ensure all dependencies are installed

## 🎉 You're Ready!

Your Order Flow Visualizer is now powered by:
- **Official DhanHQ SDK** for reliable market data
- **Supabase** for persistent storage
- **Enterprise-grade** architecture

Happy trading! 📈
