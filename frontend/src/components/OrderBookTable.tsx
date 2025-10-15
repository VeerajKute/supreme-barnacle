import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { OrderBookTableProps, OrderBookLevel } from '../types';

const OrderBookTable: React.FC<OrderBookTableProps> = ({ 
  bids, 
  asks, 
  isPaused 
}) => {
  const [maxQuantity, setMaxQuantity] = useState(0);
  const [lastUpdate, setLastUpdate] = useState<number>(Date.now());

  // Calculate maximum quantity for bar scaling
  useEffect(() => {
    const allQuantities = [...bids, ...asks].map(level => level.total);
    const max = Math.max(...allQuantities, 1);
    setMaxQuantity(max);
    setLastUpdate(Date.now());
  }, [bids, asks]);

  // Format price for display
  const formatPrice = (price: number) => {
    return price.toFixed(2);
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

  // Calculate bar width percentage
  const getBarWidth = (total: number) => {
    return Math.min((total / maxQuantity) * 100, 100);
  };

  // Render order book level
  const renderLevel = (
    level: OrderBookLevel, 
    index: number, 
    isBid: boolean
  ) => {
    const barWidth = getBarWidth(level.total);
    const isTopLevel = index === 0;
    
    return (
      <motion.tr
        key={`${isBid ? 'bid' : 'ask'}-${level.price}-${index}`}
        initial={{ opacity: 0, x: isBid ? -20 : 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: isBid ? -20 : 20 }}
        transition={{ duration: 0.2 }}
        className={`
          relative h-6 text-xs font-mono
          ${isTopLevel ? 'bg-gray-700 bg-opacity-50' : ''}
          ${isBid ? 'hover:bg-blue-900 hover:bg-opacity-30' : 'hover:bg-red-900 hover:bg-opacity-30'}
        `}
      >
        <td className="px-2 py-1 text-right">
          <span className={`
            ${isBid ? 'text-green-400' : 'text-red-400'}
            ${isTopLevel ? 'font-semibold' : ''}
          `}>
            {formatPrice(level.price)}
          </span>
        </td>
        
        <td className="px-2 py-1 text-right">
          <span className="text-gray-300">
            {formatQuantity(level.quantity)}
          </span>
        </td>
        
        <td className="px-2 py-1 text-right">
          <span className="text-gray-400">
            {formatQuantity(level.total)}
          </span>
        </td>
        
        {/* Volume bar */}
        <td className="relative w-20">
          <div className="absolute inset-0 flex items-center">
            <div
              className={`
                h-3 rounded-sm transition-all duration-200
                ${isBid 
                  ? 'bg-gradient-to-r from-green-600 to-green-400' 
                  : 'bg-gradient-to-r from-red-600 to-red-400'
                }
                ${isTopLevel ? 'opacity-100' : 'opacity-70'}
              `}
              style={{ width: `${barWidth}%` }}
            />
          </div>
        </td>
      </motion.tr>
    );
  };

  // Get top 10 levels for each side
  const topBids = bids.slice(0, 10).reverse(); // Show best bids first
  const topAsks = asks.slice(0, 10);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 px-3 py-2 border-b border-gray-700">
        <div className="grid grid-cols-4 gap-2 text-xs font-semibold text-gray-400">
          <div className="text-right">Price</div>
          <div className="text-right">Qty</div>
          <div className="text-right">Total</div>
          <div className="text-left">Volume</div>
        </div>
      </div>

      {/* Order Book Content */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full flex">
          {/* Asks (Sell Orders) */}
          <div className="flex-1">
            <div className="h-1/2 overflow-y-auto">
              <table className="w-full">
                <tbody>
                  <AnimatePresence mode="popLayout">
                    {topAsks.map((ask, index) => 
                      renderLevel(ask, index, false)
                    )}
                  </AnimatePresence>
                </tbody>
              </table>
            </div>
            
            {/* Spread */}
            <div className="h-8 flex items-center justify-center border-t border-b border-gray-600 bg-gray-800">
              <div className="text-center">
                <div className="text-xs text-gray-400">Spread</div>
                <div className="text-sm font-semibold text-yellow-400">
                  {bids.length > 0 && asks.length > 0 
                    ? (asks[0].price - bids[0].price).toFixed(2)
                    : '0.00'
                  }
                </div>
              </div>
            </div>
            
            {/* Bids (Buy Orders) */}
            <div className="h-1/2 overflow-y-auto">
              <table className="w-full">
                <tbody>
                  <AnimatePresence mode="popLayout">
                    {topBids.map((bid, index) => 
                      renderLevel(bid, index, true)
                    )}
                  </AnimatePresence>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Stats */}
      <div className="bg-gray-800 px-3 py-2 border-t border-gray-700">
        <div className="flex justify-between text-xs text-gray-400">
          <div>
            <span className="text-green-400">Bids: </span>
            <span>{bids.length}</span>
          </div>
          <div>
            <span className="text-red-400">Asks: </span>
            <span>{asks.length}</span>
          </div>
          <div>
            <span className="text-gray-400">Updated: </span>
            <span>{new Date(lastUpdate).toLocaleTimeString()}</span>
          </div>
        </div>
        
        {isPaused && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-1 text-center"
          >
            <span className="text-yellow-400 text-xs font-semibold">
              ⏸️ PAUSED
            </span>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default OrderBookTable;
