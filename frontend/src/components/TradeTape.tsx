import React, { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TradeTapeProps, TradeData } from '../types';

const TradeTape: React.FC<TradeTapeProps> = ({ 
  trades, 
  isPaused 
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [filteredTrades, setFilteredTrades] = useState<TradeData[]>([]);
  const [minVolume, setMinVolume] = useState(0);

  // Filter trades based on minimum volume
  useEffect(() => {
    const filtered = trades.filter(trade => trade.quantity >= minVolume);
    setFilteredTrades(filtered);
  }, [trades, minVolume]);

  // Auto-scroll to bottom when new trades arrive
  useEffect(() => {
    if (autoScroll && scrollRef.current && !isPaused) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [filteredTrades, autoScroll, isPaused]);

  // Handle scroll events to detect user scrolling
  const handleScroll = () => {
    if (!scrollRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
    setAutoScroll(isAtBottom);
  };

  // Format time for display
  const formatTime = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      fractionalSecondDigits: 3
    });
  };

  // Format quantity for display
  const formatQuantity = (quantity: number) => {
    if (quantity >= 1000000) {
      return `${(quantity / 1000000).toFixed(1)}M`;
    } else if (quantity >= 1000) {
      return `${(quantity / 1000).toFixed(1)}K`;
    }
    return quantity.toString();
  };

  // Get trade side color and icon
  const getTradeStyle = (side: 'buy' | 'sell') => {
    if (side === 'buy') {
      return {
        color: 'text-green-400',
        bgColor: 'bg-green-900 bg-opacity-20',
        borderColor: 'border-green-500',
        icon: '▲'
      };
    } else {
      return {
        color: 'text-red-400',
        bgColor: 'bg-red-900 bg-opacity-20',
        borderColor: 'border-red-500',
        icon: '▼'
      };
    }
  };

  // Render individual trade
  const renderTrade = (trade: TradeData, index: number) => {
    const style = getTradeStyle(trade.side);
    const isRecent = Date.now() - (trade.timestamp * 1000) < 5000; // Highlight recent trades
    
    return (
      <motion.div
        key={`${trade.timestamp}-${index}`}
        initial={{ opacity: 0, y: -20, scale: 0.95 }}
        animate={{ 
          opacity: 1, 
          y: 0, 
          scale: 1,
          backgroundColor: isRecent ? 'rgba(59, 130, 246, 0.1)' : 'transparent'
        }}
        exit={{ opacity: 0, y: 20, scale: 0.95 }}
        transition={{ 
          duration: 0.3,
          backgroundColor: { duration: 2 }
        }}
        className={`
          flex items-center justify-between px-3 py-2 text-xs font-mono
          border-l-2 ${style.borderColor}
          ${isRecent ? 'bg-blue-900 bg-opacity-10' : ''}
          hover:bg-gray-800 hover:bg-opacity-50
        `}
      >
        {/* Time */}
        <div className="text-gray-400 w-16">
          {formatTime(trade.timestamp)}
        </div>
        
        {/* Price */}
        <div className={`font-semibold w-20 text-right ${style.color}`}>
          {trade.price.toFixed(2)}
        </div>
        
        {/* Quantity */}
        <div className="text-gray-300 w-16 text-right">
          {formatQuantity(trade.quantity)}
        </div>
        
        {/* Side Icon */}
        <div className={`w-6 text-center ${style.color}`}>
          {style.icon}
        </div>
        
        {/* Trade Count (if available) */}
        {trade.tradeCount && trade.tradeCount > 1 && (
          <div className="text-gray-500 w-8 text-right">
            {trade.tradeCount}
          </div>
        )}
      </motion.div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 px-3 py-2 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="text-xs font-semibold text-gray-300">
            Trade Tape ({filteredTrades.length})
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setAutoScroll(!autoScroll)}
              className={`text-xs px-2 py-1 rounded ${
                autoScroll 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-600 text-gray-300'
              }`}
            >
              Auto
            </button>
            {isPaused && (
              <span className="text-yellow-400 text-xs">⏸️</span>
            )}
          </div>
        </div>
      </div>

      {/* Trade List */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto"
        onScroll={handleScroll}
      >
        <div className="space-y-0">
          <AnimatePresence mode="popLayout">
            {filteredTrades.map((trade, index) => 
              renderTrade(trade, index)
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Footer Controls */}
      <div className="bg-gray-800 px-3 py-2 border-t border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <label className="text-xs text-gray-400">Min Vol:</label>
            <input
              type="number"
              value={minVolume}
              onChange={(e) => setMinVolume(parseInt(e.target.value) || 0)}
              className="w-16 bg-gray-700 text-white text-xs px-2 py-1 rounded border border-gray-600"
              placeholder="0"
            />
          </div>
          
          <div className="text-xs text-gray-400">
            {autoScroll ? 'Auto-scroll ON' : 'Auto-scroll OFF'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeTape;
