# Real-Time Order Flow Visualizer for Indian Equities

A Bookmap-style live visualization system for Indian equity markets using DhanHQ APIs.

## Features

- **Real-time Order Flow Visualization**: Live heatmap showing liquidity intensity
- **20-Level Depth of Market (DOM)**: Real-time bid/ask updates
- **Trade Tape**: Vertical scroll of all trades with color-coded aggressor sides
- **Iceberg Detection**: Identify hidden liquidity patterns
- **Low Latency**: <300ms end-to-end processing

## Tech Stack

- **Backend**: Python + FastAPI + WebSocket
- **Frontend**: React + TypeScript + D3.js
- **Data Source**: DhanHQ WebSocket APIs
- **Visualization**: Canvas-based heatmap + DOM table

## Quick Start

### Prerequisites

- Python 3.8+ with pip
- Node.js 16+ with npm
- DhanHQ API credentials

### 1. Environment Setup

```bash
# Clone and navigate to project
cd Stock_terminal

# Set up environment variables
cp env.example .env
# Edit .env with your DhanHQ API credentials:
# DHAN_API_KEY=your_api_key_here
# DHAN_API_SECRET=your_api_secret_here
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend (Terminal 1)
python start_backend.py
# OR manually:
# cd backend
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
# Start the frontend (Terminal 2)
# Windows:
start_frontend.bat

# Linux/Mac:
./start_frontend.sh

# OR manually:
# cd frontend
# npm install
# npm start
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws
- **API Docs**: http://localhost:8000/docs

## Configuration

1. Copy `env.example` to `.env`
2. Add your DhanHQ API credentials
3. Configure symbol selection in the frontend dropdown
4. Adjust aggregation settings as needed

## Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐    WebSocket    ┌─────────────────┐
│   DhanHQ APIs   │ ──────────────► │  Python Backend │ ──────────────► │  React Frontend │
│  (Market Data)  │                 │  (FastAPI + WS) │                 │  (Visualization)│
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
```

## Components

- **HeatmapCanvas**: Order flow liquidity visualization
- **OrderBookTable**: 20-level DOM display
- **TradeTape**: Vertical trade history
- **SettingsPanel**: Symbol and configuration controls

## Performance

- Target latency: <300ms end-to-end
- Update frequency: 100-200ms
- Smooth animations with Framer Motion
- Optimized rendering with Canvas and D3.js
