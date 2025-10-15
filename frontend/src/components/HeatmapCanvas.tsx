import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { motion } from 'framer-motion';
import { HeatmapCanvasProps, HeatmapPoint, HeatmapConfig } from '../types';

const HeatmapCanvas: React.FC<HeatmapCanvasProps> = ({ 
  marketData, 
  trades, 
  isPaused 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [config, setConfig] = useState<HeatmapConfig>({
    width: 800,
    height: 600,
    priceRange: { min: 0, max: 0 },
    timeRange: 300000, // 5 minutes
    colorScheme: 'blue-red',
    bubbleSize: 'medium'
  });

  // Animation frame reference
  const animationFrameRef = useRef<number>();
  const lastRenderTimeRef = useRef<number>(0);

  // Update dimensions on resize
  const updateDimensions = useCallback(() => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setDimensions({ width: rect.width, height: rect.height });
      setConfig(prev => ({
        ...prev,
        width: rect.width,
        height: rect.height
      }));
    }
  }, []);

  // Calculate price range from market data
  const calculatePriceRange = useCallback(() => {
    if (!marketData || !marketData.bids.length || !marketData.asks.length) {
      return { min: 0, max: 0 };
    }

    const allPrices = [
      ...marketData.bids.map(([price]) => price),
      ...marketData.asks.map(([price]) => price)
    ];

    const minPrice = Math.min(...allPrices);
    const maxPrice = Math.max(...allPrices);
    const spread = maxPrice - minPrice;
    const padding = spread * 0.1; // 10% padding

    return {
      min: minPrice - padding,
      max: maxPrice + padding
    };
  }, [marketData]);

  // Update price range when market data changes
  useEffect(() => {
    const newPriceRange = calculatePriceRange();
    if (newPriceRange.min !== 0 || newPriceRange.max !== 0) {
      setConfig(prev => ({
        ...prev,
        priceRange: newPriceRange
      }));
    }
  }, [calculatePriceRange]);

  // Handle window resize
  useEffect(() => {
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, [updateDimensions]);

  // Color schemes
  const getColorScheme = (side: 'buy' | 'sell', intensity: number) => {
    const alpha = Math.min(intensity, 1);
    
    switch (config.colorScheme) {
      case 'blue-red':
        return side === 'buy' 
          ? `rgba(59, 130, 246, ${alpha})` // Blue for buy
          : `rgba(239, 68, 68, ${alpha})`; // Red for sell
      case 'green-red':
        return side === 'buy'
          ? `rgba(34, 197, 94, ${alpha})` // Green for buy
          : `rgba(239, 68, 68, ${alpha})`; // Red for sell
      case 'purple-orange':
        return side === 'buy'
          ? `rgba(147, 51, 234, ${alpha})` // Purple for buy
          : `rgba(249, 115, 22, ${alpha})`; // Orange for sell
      default:
        return side === 'buy'
          ? `rgba(59, 130, 246, ${alpha})`
          : `rgba(239, 68, 68, ${alpha})`;
    }
  };

  // Calculate bubble size based on volume
  const getBubbleSize = (volume: number) => {
    const maxVolume = Math.max(...trades.map(t => t.quantity), 1);
    const normalizedVolume = volume / maxVolume;
    
    const baseSize = config.bubbleSize === 'small' ? 4 : 
                    config.bubbleSize === 'medium' ? 8 : 12;
    
    return Math.max(baseSize, baseSize * normalizedVolume * 3);
  };

  // Render heatmap
  const renderHeatmap = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !config.width || !config.height) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, config.width, config.height);

    // Set canvas size
    canvas.width = config.width;
    canvas.height = config.height;

    // Create scales
    const xScale = d3.scaleLinear()
      .domain([Date.now() - config.timeRange, Date.now()])
      .range([0, config.width]);

    const yScale = d3.scaleLinear()
      .domain([config.priceRange.min, config.priceRange.max])
      .range([config.height, 0]);

    // Render background grid
    ctx.strokeStyle = 'rgba(55, 65, 81, 0.3)';
    ctx.lineWidth = 1;

    // Horizontal price lines
    const priceStep = (config.priceRange.max - config.priceRange.min) / 20;
    for (let i = 0; i <= 20; i++) {
      const price = config.priceRange.min + (priceStep * i);
      const y = yScale(price);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(config.width, y);
      ctx.stroke();
    }

    // Vertical time lines
    const timeStep = config.timeRange / 10;
    for (let i = 0; i <= 10; i++) {
      const time = Date.now() - config.timeRange + (timeStep * i);
      const x = xScale(time);
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, config.height);
      ctx.stroke();
    }

    // Render trades as bubbles
    trades.forEach(trade => {
      const x = xScale(trade.timestamp * 1000);
      const y = yScale(trade.price);
      const size = getBubbleSize(trade.quantity);
      const intensity = Math.min(trade.quantity / 1000, 1); // Normalize intensity
      const color = getColorScheme(trade.side, intensity);

      // Draw bubble
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, size, 0, 2 * Math.PI);
      ctx.fill();

      // Add subtle glow effect
      ctx.shadowColor = color;
      ctx.shadowBlur = size * 2;
      ctx.beginPath();
      ctx.arc(x, y, size * 0.7, 0, 2 * Math.PI);
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    // Render current price line if available
    if (marketData?.last_trade) {
      const currentPrice = marketData.last_trade.price;
      const y = yScale(currentPrice);
      
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(config.width, y);
      ctx.stroke();
      ctx.setLineDash([]);
    }

  }, [marketData, trades, config, isPaused]);

  // Animation loop
  useEffect(() => {
    const animate = (currentTime: number) => {
      if (currentTime - lastRenderTimeRef.current >= 100) { // 10 FPS
        if (!isPaused) {
          renderHeatmap();
        }
        lastRenderTimeRef.current = currentTime;
      }
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [renderHeatmap, isPaused]);

  // Force render when data changes
  useEffect(() => {
    if (!isPaused) {
      renderHeatmap();
    }
  }, [marketData, trades, renderHeatmap, isPaused]);

  return (
    <div ref={containerRef} className="h-full w-full relative bg-gray-900">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 bg-gray-800 bg-opacity-90 px-4 py-2 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-300">Order Flow Heatmap</h3>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-xs text-gray-400">Buy</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-xs text-gray-400">Sell</span>
            </div>
            {isPaused && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-yellow-400 text-xs font-semibold"
              >
                PAUSED
              </motion.div>
            )}
          </div>
        </div>
      </div>

      {/* Canvas */}
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ marginTop: '40px' }}
      />

      {/* Controls Overlay */}
      <div className="absolute bottom-4 right-4 z-10">
        <div className="bg-gray-800 bg-opacity-90 rounded-lg p-3 space-y-2">
          <div className="text-xs text-gray-300">Color Scheme</div>
          <select
            value={config.colorScheme}
            onChange={(e) => setConfig(prev => ({
              ...prev,
              colorScheme: e.target.value as 'blue-red' | 'green-red' | 'purple-orange'
            }))}
            className="bg-gray-700 text-white text-xs px-2 py-1 rounded border border-gray-600"
          >
            <option value="blue-red">Blue-Red</option>
            <option value="green-red">Green-Red</option>
            <option value="purple-orange">Purple-Orange</option>
          </select>
          
          <div className="text-xs text-gray-300">Bubble Size</div>
          <select
            value={config.bubbleSize}
            onChange={(e) => setConfig(prev => ({
              ...prev,
              bubbleSize: e.target.value as 'small' | 'medium' | 'large'
            }))}
            className="bg-gray-700 text-white text-xs px-2 py-1 rounded border border-gray-600"
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default HeatmapCanvas;
