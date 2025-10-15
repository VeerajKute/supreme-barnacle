# Order Flow Visualizer - Setup Guide

## 🎯 Project Overview

A real-time order flow visualizer for Indian equities using DhanHQ APIs, featuring:
- **Live heatmap visualization** with order flow intensity
- **20-level Depth of Market (DOM)** with real-time updates
- **Trade tape** with color-coded aggressor sides
- **Iceberg detection** and overflow analysis
- **Sub-300ms latency** end-to-end processing

## 📁 Project Structure

```
Stock_terminal/
├── backend/                    # Python FastAPI backend
│   ├── __init__.py
│   └── main.py                # Main WebSocket bridge
├── frontend/                  # React TypeScript frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── HeatmapCanvas.tsx
│   │   │   ├── OrderBookTable.tsx
│   │   │   ├── TradeTape.tsx
│   │   │   ├── SettingsPanel.tsx
│   │   │   └── StatusBar.tsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── requirements.txt           # Python dependencies
├── env.example              # Environment template
├── start_backend.py         # Backend startup script
├── start_frontend.bat       # Windows frontend script
├── start_frontend.sh        # Linux/Mac frontend script
├── README.md
└── SETUP.md
```

## 🚀 Quick Start (3 Steps)

### Step 1: Environment Setup
```bash
# 1. Copy environment file
cp env.example .env

# 2. Edit .env with your DhanHQ credentials
# DHAN_API_KEY=your_api_key_here
# DHAN_API_SECRET=your_api_secret_here
```

### Step 2: Start Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start backend server
python start_backend.py
```

### Step 3: Start Frontend
```bash
# Windows
start_frontend.bat

# Linux/Mac
./start_frontend.sh
```

## 🔧 Manual Setup

### Backend (Python)
```bash
cd backend
pip install fastapi uvicorn websockets pydantic aiofiles python-dotenv
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

## 🌐 Access Points

- **Main App**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

## ⚙️ Configuration

### DhanHQ API Setup
1. Get API credentials from [DhanHQ](https://dhanhq.co)
2. Add credentials to `.env` file
3. Supported symbols: RELIANCE, TCS, INFY, HDFC, ITC, etc.

### Customization Options
- **Color schemes**: Blue-Red, Green-Red, Purple-Orange
- **Bubble sizes**: Small, Medium, Large
- **Aggregation intervals**: 100ms, 500ms, 1s
- **Symbol selection**: Dropdown with 10+ NSE stocks

## 🐛 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if backend is running on port 8000
   - Verify DhanHQ API credentials
   - Check firewall settings

2. **Frontend Won't Start**
   - Ensure Node.js 16+ is installed
   - Run `npm install` in frontend directory
   - Check for port 3000 conflicts

3. **No Market Data**
   - Verify DhanHQ API key and secret
   - Check market hours (9:15 AM - 3:30 PM IST)
   - Try different symbols

### Performance Optimization

- **Latency**: Target <300ms end-to-end
- **Memory**: ~100MB for backend, ~200MB for frontend
- **CPU**: Minimal impact with efficient rendering
- **Network**: WebSocket connection with auto-reconnect

## 📊 Features

### Real-time Visualization
- ✅ Live order flow heatmap
- ✅ 20-level DOM table
- ✅ Trade tape with timestamps
- ✅ Iceberg order detection
- ✅ Volume-based bubble sizing
- ✅ Color-coded aggressor sides

### Interactive Controls
- ✅ Symbol selection dropdown
- ✅ Play/Pause functionality
- ✅ Color scheme switching
- ✅ Bubble size adjustment
- ✅ Auto-scroll trade tape
- ✅ Volume filtering

### Performance Features
- ✅ Smooth animations (Framer Motion)
- ✅ Efficient Canvas rendering
- ✅ WebSocket auto-reconnect
- ✅ Latency monitoring
- ✅ Message count tracking

## 🔒 Security Notes

- API credentials stored in `.env` file
- WebSocket connections use authentication headers
- No sensitive data logged to console
- CORS configured for localhost only

## 📈 Next Steps

1. **Add more symbols** to NSE_SYMBOLS in types/index.ts
2. **Implement replay mode** for historical data
3. **Add cumulative delta** indicator
4. **Create imbalance ratio** visualization
5. **Add drag-and-drop** panel resizing

## 🆘 Support

- Check console logs for errors
- Verify all dependencies are installed
- Ensure ports 3000 and 8000 are available
- Test with different symbols during market hours
