import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Plus, TrendingUp, Clock, Star } from 'lucide-react';

interface SymbolInfo {
  symbol: string;
  token: string;
  name: string;
  sector?: string;
  market_cap?: string;
}

interface DynamicSymbolSearchProps {
  onSymbolSelect: (symbol: string) => void;
  selectedSymbol: string;
  isConnected: boolean;
}

const DynamicSymbolSearch: React.FC<DynamicSymbolSearchProps> = ({
  onSymbolSelect,
  selectedSymbol,
  isConnected
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SymbolInfo[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [recentSymbols, setRecentSymbols] = useState<string[]>([]);
  const [popularSymbols, setPopularSymbols] = useState<SymbolInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout>();

  // Load recent symbols from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('recent_symbols');
    if (saved) {
      setRecentSymbols(JSON.parse(saved));
    }
  }, []);

  // Load popular symbols on mount
  useEffect(() => {
    loadPopularSymbols();
  }, []);

  // Handle click outside to close results
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadPopularSymbols = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/symbols/popular?limit=20');
      const data = await response.json();
      setPopularSymbols(data.symbols || []);
    } catch (error) {
      console.error('Error loading popular symbols:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const searchSymbols = async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setResults([]);
      return;
    }

    try {
      setIsSearching(true);
      const response = await fetch(
        `http://localhost:8000/symbols/search?q=${encodeURIComponent(searchQuery)}&limit=20`
      );
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error('Error searching symbols:', error);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleInputChange = (value: string) => {
    setQuery(value);
    setShowResults(true);

    // Clear existing timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Debounce search
    searchTimeoutRef.current = setTimeout(() => {
      searchSymbols(value);
    }, 300);
  };

  const handleSymbolSelect = (symbol: string) => {
    onSymbolSelect(symbol);
    setQuery('');
    setShowResults(false);
    
    // Add to recent symbols
    const newRecent = [symbol, ...recentSymbols.filter(s => s !== symbol)].slice(0, 10);
    setRecentSymbols(newRecent);
    localStorage.setItem('recent_symbols', JSON.stringify(newRecent));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setShowResults(false);
      setQuery('');
    } else if (e.key === 'Enter' && query) {
      handleSymbolSelect(query.toUpperCase());
    }
  };

  const formatMarketCap = (marketCap: string) => {
    if (!marketCap) return '';
    const num = parseFloat(marketCap);
    if (num >= 1000000000000) return `${(num / 1000000000000).toFixed(1)}T`;
    if (num >= 1000000000) return `${(num / 1000000000).toFixed(1)}B`;
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    return marketCap;
  };

  return (
    <div ref={searchRef} className="relative w-full">
      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-4 w-4 text-gray-400" />
        </div>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => handleInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowResults(true)}
          placeholder="Search any NSE symbol (e.g., RELIANCE, TCS, HDFC)..."
          className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {isSearching && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          </div>
        )}
      </div>

      {/* Search Results */}
      <AnimatePresence>
        {showResults && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 right-0 mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-xl z-50 max-h-96 overflow-y-auto"
          >
            {/* Recent Symbols */}
            {!query && recentSymbols.length > 0 && (
              <div className="p-3 border-b border-gray-600">
                <div className="flex items-center space-x-2 text-sm text-gray-400 mb-2">
                  <Clock className="h-4 w-4" />
                  <span>Recent</span>
                </div>
                <div className="space-y-1">
                  {recentSymbols.slice(0, 5).map((symbol) => (
                    <button
                      key={symbol}
                      onClick={() => handleSymbolSelect(symbol)}
                      className="w-full text-left px-3 py-2 hover:bg-gray-700 rounded text-sm text-white"
                    >
                      {symbol}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Popular Symbols */}
            {!query && popularSymbols.length > 0 && (
              <div className="p-3 border-b border-gray-600">
                <div className="flex items-center space-x-2 text-sm text-gray-400 mb-2">
                  <TrendingUp className="h-4 w-4" />
                  <span>Popular</span>
                </div>
                <div className="space-y-1">
                  {popularSymbols.slice(0, 10).map((symbol) => (
                    <button
                      key={symbol.symbol}
                      onClick={() => handleSymbolSelect(symbol.symbol)}
                      className="w-full text-left px-3 py-2 hover:bg-gray-700 rounded text-sm"
                    >
                      <div className="flex justify-between items-center">
                        <span className="text-white font-medium">{symbol.symbol}</span>
                        <span className="text-gray-400 text-xs">{symbol.name}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Search Results */}
            {query && (
              <div className="p-3">
                <div className="flex items-center space-x-2 text-sm text-gray-400 mb-2">
                  <Search className="h-4 w-4" />
                  <span>Search Results</span>
                  {results.length > 0 && (
                    <span className="text-xs">({results.length} found)</span>
                  )}
                </div>
                
                {isSearching ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                    <span className="ml-2 text-sm text-gray-400">Searching...</span>
                  </div>
                ) : results.length > 0 ? (
                  <div className="space-y-1">
                    {results.map((result) => (
                      <button
                        key={result.symbol}
                        onClick={() => handleSymbolSelect(result.symbol)}
                        className="w-full text-left px-3 py-2 hover:bg-gray-700 rounded text-sm"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="text-white font-medium">{result.symbol}</div>
                            <div className="text-gray-400 text-xs">{result.name}</div>
                            {result.sector && (
                              <div className="text-gray-500 text-xs">{result.sector}</div>
                            )}
                          </div>
                          {result.market_cap && (
                            <div className="text-xs text-gray-400">
                              {formatMarketCap(result.market_cap)}
                            </div>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <div className="text-gray-400 text-sm">No symbols found</div>
                    <div className="text-gray-500 text-xs mt-1">
                      Try searching for a different symbol
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Connection Status */}
            {!isConnected && (
              <div className="p-3 border-t border-gray-600 bg-red-900 bg-opacity-20">
                <div className="text-red-400 text-sm">
                  ⚠️ Not connected to server. Some features may be limited.
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DynamicSymbolSearch;
