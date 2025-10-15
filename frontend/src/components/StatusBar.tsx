import React from 'react';
import { motion } from 'framer-motion';
import { StatusBarProps } from '../types';
import { Wifi, WifiOff, Clock, Activity } from 'lucide-react';

const StatusBar: React.FC<StatusBarProps> = ({
  isConnected,
  latency,
  messageCount,
  selectedSymbol
}) => {
  const formatLatency = (ms: number) => {
    if (ms < 1000) {
      return `${ms}ms`;
    }
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const getLatencyColor = (ms: number) => {
    if (ms < 100) return 'text-green-400';
    if (ms < 300) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getConnectionStatus = () => {
    if (isConnected) {
      return {
        icon: Wifi,
        text: 'Connected',
        color: 'text-green-400',
        bgColor: 'bg-green-900 bg-opacity-20'
      };
    } else {
      return {
        icon: WifiOff,
        text: 'Disconnected',
        color: 'text-red-400',
        bgColor: 'bg-red-900 bg-opacity-20'
      };
    }
  };

  const connectionStatus = getConnectionStatus();
  const StatusIcon = connectionStatus.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-800 border-b border-gray-700 px-4 py-2"
    >
      <div className="flex items-center justify-between">
        {/* Left side - Connection status */}
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-lg ${connectionStatus.bgColor}`}>
            <StatusIcon className="w-4 h-4" />
            <span className={`text-sm font-medium ${connectionStatus.color}`}>
              {connectionStatus.text}
            </span>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <span>Symbol:</span>
            <span className="text-white font-semibold">{selectedSymbol}</span>
          </div>
        </div>

        {/* Center - Latency */}
        <div className="flex items-center space-x-2">
          <Clock className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400">Latency:</span>
          <motion.span
            key={latency}
            initial={{ scale: 1.2, opacity: 0.7 }}
            animate={{ scale: 1, opacity: 1 }}
            className={`text-sm font-mono font-semibold ${getLatencyColor(latency)}`}
          >
            {formatLatency(latency)}
          </motion.span>
        </div>

        {/* Right side - Message count and activity */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <Activity className="w-4 h-4" />
            <span>Messages:</span>
            <motion.span
              key={messageCount}
              initial={{ scale: 1.1 }}
              animate={{ scale: 1 }}
              className="text-white font-semibold"
            >
              {messageCount.toLocaleString()}
            </motion.span>
          </div>

          {/* Data flow indicator */}
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              {[...Array(3)].map((_, i) => (
                <motion.div
                  key={i}
                  animate={{
                    opacity: isConnected ? [0.3, 1, 0.3] : 0.3,
                    scale: isConnected ? [0.8, 1.2, 0.8] : 0.8
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    delay: i * 0.2
                  }}
                  className="w-2 h-2 bg-blue-400 rounded-full"
                />
              ))}
            </div>
            <span className="text-xs text-gray-400">
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default StatusBar;
