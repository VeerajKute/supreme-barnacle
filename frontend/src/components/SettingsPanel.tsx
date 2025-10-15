import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { SettingsPanelProps } from '../types';
import { Play, Pause, Settings, ChevronDown, Search } from 'lucide-react';
import DynamicSymbolSearch from './DynamicSymbolSearch';

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  selectedSymbol,
  onSymbolChange,
  isPaused,
  onPauseToggle
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      {/* Settings Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded-lg transition-colors"
      >
        <Settings className="w-4 h-4" />
        <span className="text-sm">Settings</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </motion.button>

      {/* Settings Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full right-0 mt-2 w-80 bg-gray-800 border border-gray-600 rounded-lg shadow-xl z-50"
          >
            <div className="p-4 space-y-4">
              {/* Symbol Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Symbol Search
                </label>
                <DynamicSymbolSearch
                  onSymbolSelect={onSymbolChange}
                  selectedSymbol={selectedSymbol}
                  isConnected={true} // You can pass actual connection status
                />
                <div className="mt-2 text-xs text-gray-400">
                  💡 Type any NSE symbol to search and discover automatically
                </div>
              </div>

              {/* Play/Pause Controls */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Controls
                </label>
                <div className="flex items-center space-x-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={onPauseToggle}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                      isPaused 
                        ? 'bg-green-600 hover:bg-green-700 text-white' 
                        : 'bg-red-600 hover:bg-red-700 text-white'
                    }`}
                  >
                    {isPaused ? (
                      <>
                        <Play className="w-4 h-4" />
                        <span>Resume</span>
                      </>
                    ) : (
                      <>
                        <Pause className="w-4 h-4" />
                        <span>Pause</span>
                      </>
                    )}
                  </motion.button>
                  
                  <div className="text-xs text-gray-400">
                    {isPaused ? 'Data flow paused' : 'Live data streaming'}
                  </div>
                </div>
              </div>

              {/* Connection Status */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Status
                </label>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">Connection:</span>
                    <span className="text-green-400">Connected</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">Symbol:</span>
                    <span className="text-white">{selectedSymbol}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">Status:</span>
                    <span className={isPaused ? 'text-yellow-400' : 'text-green-400'}>
                      {isPaused ? 'Paused' : 'Live'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Quick Actions
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      // Reset view to current symbol
                      onSymbolChange(selectedSymbol);
                    }}
                    className="bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded text-xs transition-colors"
                  >
                    Reset View
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      // Clear all data
                      window.location.reload();
                    }}
                    className="bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded text-xs transition-colors"
                  >
                    Clear Data
                  </motion.button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default SettingsPanel;
