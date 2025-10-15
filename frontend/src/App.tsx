import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWebSocket } from './hooks/useWebSocket';
import HeatmapCanvas from './components/HeatmapCanvas';
import OrderBookTable from './components/OrderBookTable';
import TradeTape from './components/TradeTape';
import SettingsPanel from './components/SettingsPanel';
import StatusBar from './components/StatusBar';
import OffMarketVisualizer from './components/OffMarketVisualizer';
import { MarketData, TradeData, OrderBookLevel } from './types';

const App: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('RELIANCE');
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [trades, setTrades] = useState<TradeData[]>([]);
  const [orderBook, setOrderBook] = useState<{
    bids: OrderBookLevel[];
    asks: OrderBookLevel[];
  }>({ bids: [], asks: [] });
  
  // Off-market mode state
  const [isMarketHours, setIsMarketHours] = useState<boolean>(true);
  const [offMarketData, setOffMarketData] = useState<any>(null);
  const [currentTimeframe, setCurrentTimeframe] = useState<string>('1min');

  // WebSocket connection
  const { 
    socket, 
    isConnected, 
    latency, 
    messageCount 
  } = useWebSocket('ws://localhost:8000/ws');

  // Handle WebSocket messages
  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event: MessageEvent) => {
      if (isPaused) return;

      try {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'market_status':
            setIsMarketHours(data.is_market_hours);
            break;
            
          case 'off_market_data':
            setOffMarketData(data);
            break;
            
          case 'depth_update':
            setMarketData(data);
            setOrderBook({
              bids: data.bids?.map(([price, qty]: [number, number]) => ({
                price,
                quantity: qty,
                total: 0 // Will be calculated
              })) || [],
              asks: data.asks?.map(([price, qty]: [number, number]) => ({
                price,
                quantity: qty,
                total: 0 // Will be calculated
              })) || []
            });
            break;
            
          case 'aggregated_trades':
            if (data.data) {
              const newTrades: TradeData[] = Object.entries(data.data).map(([price, tradeData]: [string, any]) => ({
                price: parseFloat(price),
                quantity: tradeData.total_volume,
                side: tradeData.buy_volume > tradeData.sell_volume ? 'buy' : 'sell',
                timestamp: data.timestamp,
                tradeCount: tradeData.trade_count
              }));
              
              setTrades(prev => [...newTrades, ...prev.slice(0, 500)]); // Keep last 500 trades
            }
            break;
            
          case 'symbol_changed':
            setSelectedSymbol(data.symbol);
            break;
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    socket.addEventListener('message', handleMessage);
    
    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket, isPaused]);

  // Send symbol change request
  const handleSymbolChange = (symbol: string) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'change_symbol',
        symbol
      }));
    }
  };

  // Handle timeframe change for off-market mode
  const handleTimeframeChange = (timeframe: string) => {
    setCurrentTimeframe(timeframe);
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'change_timeframe',
        timeframe
      }));
    }
  };

  // Calculate cumulative quantities for order book
  const calculateCumulativeQuantities = (levels: OrderBookLevel[]) => {
    let cumulative = 0;
    return levels.map(level => {
      cumulative += level.quantity;
      return { ...level, total: cumulative };
    });
  };

  const bidsWithTotal = calculateCumulativeQuantities(orderBook.bids);
  const asksWithTotal = calculateCumulativeQuantities(orderBook.asks);

  return (
    <div className="h-screen w-screen bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between"
      >
        <h1 className="text-xl font-bold text-blue-400">
          Order Flow Visualizer
        </h1>
        <div className="flex items-center space-x-4">
          <SettingsPanel
            selectedSymbol={selectedSymbol}
            onSymbolChange={handleSymbolChange}
            isPaused={isPaused}
            onPauseToggle={() => setIsPaused(!isPaused)}
          />
        </div>
      </motion.div>

      {/* Status Bar */}
      <StatusBar
        isConnected={isConnected}
        latency={latency}
        messageCount={messageCount}
        selectedSymbol={selectedSymbol}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {isMarketHours ? (
          // Live market mode
          <>
            {/* Left Panel - Heatmap */}
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex-1 bg-gray-900 border-r border-gray-700"
            >
              <HeatmapCanvas
                marketData={marketData}
                trades={trades}
                isPaused={isPaused}
              />
            </motion.div>

            {/* Center Panel - Order Book */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-80 bg-gray-900 border-r border-gray-700 flex flex-col"
            >
              <div className="bg-gray-800 px-4 py-2 border-b border-gray-700">
                <h2 className="text-sm font-semibold text-gray-300">Order Book</h2>
                <p className="text-xs text-gray-400">{selectedSymbol}</p>
              </div>
              <OrderBookTable
                bids={bidsWithTotal}
                asks={asksWithTotal}
                isPaused={isPaused}
              />
            </motion.div>

            {/* Right Panel - Trade Tape */}
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="w-80 bg-gray-900 flex flex-col"
            >
              <div className="bg-gray-800 px-4 py-2 border-b border-gray-700">
                <h2 className="text-sm font-semibold text-gray-300">Trade Tape</h2>
                <p className="text-xs text-gray-400">Time & Sales</p>
              </div>
              <TradeTape
                trades={trades}
                isPaused={isPaused}
              />
            </motion.div>
          </>
        ) : (
          // Off-market mode
          <div className="flex-1 bg-gray-900 overflow-y-auto">
            {offMarketData ? (
              <OffMarketVisualizer
                data={offMarketData}
                onTimeframeChange={handleTimeframeChange}
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
                  <p className="text-gray-400">Loading historical data...</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Connection Status Overlay */}
      <AnimatePresence>
        {!isConnected && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          >
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-600">
              <h3 className="text-lg font-semibold text-red-400 mb-2">
                Connection Lost
              </h3>
              <p className="text-gray-300">
                Reconnecting to WebSocket server...
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default App;
