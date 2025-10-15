import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Clock, BarChart3, TrendingUp, Volume2 } from 'lucide-react';
import * as d3 from 'd3';

interface HistoricalCandle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ohlc: number[];
}

interface VolumeProfile {
  price: number;
  volume: number;
  buy_volume: number;
  sell_volume: number;
  timestamp: number;
}

interface OffMarketData {
  type: string;
  symbol: string;
  timeframe: string;
  candles: HistoricalCandle[];
  volume_profile: VolumeProfile[];
  order_flow: any[];
  market_depth: {
    bids: number[][];
    asks: number[][];
    last_trade: {
      price: number;
      quantity: number;
      side: string;
    };
  };
  timestamp: number;
  market_status: string;
}

interface OffMarketVisualizerProps {
  data: OffMarketData;
  onTimeframeChange: (timeframe: string) => void;
}

const OffMarketVisualizer: React.FC<OffMarketVisualizerProps> = ({
  data,
  onTimeframeChange
}) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1min');
  const [showVolumeProfile, setShowVolumeProfile] = useState(true);
  const [showOrderFlow, setShowOrderFlow] = useState(true);
  
  const candleChartRef = useRef<HTMLDivElement>(null);
  const volumeChartRef = useRef<HTMLDivElement>(null);
  const orderFlowRef = useRef<HTMLDivElement>(null);

  const timeframes = [
    { value: '1min', label: '1 Min', description: '1 minute candles' },
    { value: '5min', label: '5 Min', description: '5 minute candles' },
    { value: '15min', label: '15 Min', description: '15 minute candles' },
    { value: '1hour', label: '1 Hour', description: '1 hour candles' },
    { value: '1day', label: '1 Day', description: 'Daily candles' }
  ];

  useEffect(() => {
    if (data.candles && candleChartRef.current) {
      renderCandleChart();
    }
  }, [data.candles]);

  useEffect(() => {
    if (data.volume_profile && volumeChartRef.current && showVolumeProfile) {
      renderVolumeProfile();
    }
  }, [data.volume_profile, showVolumeProfile]);

  useEffect(() => {
    if (data.order_flow && orderFlowRef.current && showOrderFlow) {
      renderOrderFlow();
    }
  }, [data.order_flow, showOrderFlow]);

  const renderCandleChart = () => {
    if (!candleChartRef.current || !data.candles.length) return;

    const container = candleChartRef.current;
    container.innerHTML = '';

    const margin = { top: 20, right: 20, bottom: 40, left: 60 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Scale data
    const xScale = d3.scaleBand()
      .domain(data.candles.map((_, i) => i.toString()))
      .range([0, width])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain(d3.extent(data.candles, d => [d.high, d.low]).flat() as [number, number])
      .range([height, 0]);

    // Color scale for candles
    const colorScale = (candle: HistoricalCandle) => 
      candle.close > candle.open ? '#10b981' : '#ef4444';

    // Draw candles
    g.selectAll('.candle')
      .data(data.candles)
      .enter()
      .append('rect')
      .attr('class', 'candle')
      .attr('x', (_, i) => xScale(i.toString())!)
      .attr('y', d => yScale(Math.max(d.open, d.close)))
      .attr('width', xScale.bandwidth())
      .attr('height', d => Math.abs(yScale(d.close) - yScale(d.open)))
      .attr('fill', colorScale)
      .attr('stroke', colorScale)
      .attr('stroke-width', 1);

    // Draw wicks
    g.selectAll('.wick')
      .data(data.candles)
      .enter()
      .append('line')
      .attr('class', 'wick')
      .attr('x1', (_, i) => xScale(i.toString())! + xScale.bandwidth() / 2)
      .attr('x2', (_, i) => xScale(i.toString())! + xScale.bandwidth() / 2)
      .attr('y1', d => yScale(d.high))
      .attr('y2', d => yScale(d.low))
      .attr('stroke', colorScale)
      .attr('stroke-width', 1);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickFormat((_, i) => {
        const candle = data.candles[parseInt(i.toString())];
        return new Date(candle.timestamp * 1000).toLocaleTimeString();
      }));

    g.append('g')
      .call(d3.axisLeft(yScale).tickFormat(d3.format('.2f')));
  };

  const renderVolumeProfile = () => {
    if (!volumeChartRef.current || !data.volume_profile.length) return;

    const container = volumeChartRef.current;
    container.innerHTML = '';

    const margin = { top: 20, right: 20, bottom: 40, left: 60 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = 200 - margin.top - margin.bottom;

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Scale data
    const xScale = d3.scaleBand()
      .domain(data.volume_profile.map((_, i) => i.toString()))
      .range([0, width])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data.volume_profile, d => d.volume)!])
      .range([height, 0]);

    // Draw volume bars
    g.selectAll('.volume-bar')
      .data(data.volume_profile)
      .enter()
      .append('rect')
      .attr('class', 'volume-bar')
      .attr('x', (_, i) => xScale(i.toString())!)
      .attr('y', d => yScale(d.volume))
      .attr('width', xScale.bandwidth())
      .attr('height', d => height - yScale(d.volume))
      .attr('fill', d => d.buy_volume > d.sell_volume ? '#10b981' : '#ef4444')
      .attr('opacity', 0.7);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickFormat((_, i) => {
        const profile = data.volume_profile[parseInt(i.toString())];
        return profile.price.toFixed(2);
      }));

    g.append('g')
      .call(d3.axisLeft(yScale).tickFormat(d3.format('.2s')));
  };

  const renderOrderFlow = () => {
    if (!orderFlowRef.current || !data.order_flow.length) return;

    const container = orderFlowRef.current;
    container.innerHTML = '';

    const maxTicks = 50;
    const recentTicks = data.order_flow.slice(-maxTicks);

    recentTicks.forEach((tick, index) => {
      const tickElement = document.createElement('div');
      tickElement.className = `flex items-center justify-between p-2 mb-1 rounded ${
        tick.side === 'buy' ? 'bg-green-900/20 border-l-2 border-green-500' : 'bg-red-900/20 border-l-2 border-red-500'
      }`;
      
      tickElement.innerHTML = `
        <div class="flex items-center space-x-2">
          <span class="text-xs text-gray-400">${new Date(tick.timestamp * 1000).toLocaleTimeString()}</span>
          <span class="font-mono text-sm">${tick.price.toFixed(2)}</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-xs">${tick.quantity}</span>
          <span class="text-xs ${tick.side === 'buy' ? 'text-green-400' : 'text-red-400'}">${tick.side.toUpperCase()}</span>
        </div>
      `;
      
      container.appendChild(tickElement);
    });
  };

  const handleTimeframeChange = (timeframe: string) => {
    setSelectedTimeframe(timeframe);
    onTimeframeChange(timeframe);
  };

  return (
    <div className="space-y-6">
      {/* Market Status Header */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Clock className="w-5 h-5 text-yellow-400" />
            <div>
              <h3 className="text-lg font-semibold text-white">Market Closed</h3>
              <p className="text-sm text-gray-400">Historical Data Visualization</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-400">Symbol: {data.symbol}</p>
            <p className="text-xs text-gray-500">
              {new Date(data.timestamp * 1000).toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Timeframe Selector */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">Timeframe</h4>
        <div className="flex flex-wrap gap-2">
          {timeframes.map((tf) => (
            <button
              key={tf.value}
              onClick={() => handleTimeframeChange(tf.value)}
              className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                selectedTimeframe === tf.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Controls */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">Visualization Options</h4>
        <div className="flex flex-wrap gap-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showVolumeProfile}
              onChange={(e) => setShowVolumeProfile(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm text-gray-300">Volume Profile</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showOrderFlow}
              onChange={(e) => setShowOrderFlow(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm text-gray-300">Order Flow</span>
          </label>
        </div>
      </div>

      {/* Candle Chart */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-4">
          <BarChart3 className="w-5 h-5 text-blue-400" />
          <h4 className="text-lg font-semibold text-white">Price Chart</h4>
        </div>
        <div ref={candleChartRef} className="w-full h-96"></div>
      </div>

      {/* Volume Profile */}
      {showVolumeProfile && (
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-4">
            <Volume2 className="w-5 h-5 text-green-400" />
            <h4 className="text-lg font-semibold text-white">Volume Profile</h4>
          </div>
          <div ref={volumeChartRef} className="w-full h-48"></div>
        </div>
      )}

      {/* Order Flow */}
      {showOrderFlow && (
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-4">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            <h4 className="text-lg font-semibold text-white">Order Flow</h4>
          </div>
          <div ref={orderFlowRef} className="max-h-64 overflow-y-auto"></div>
        </div>
      )}

      {/* Market Depth Simulation */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h4 className="text-lg font-semibold text-white mb-4">Market Depth (Simulated)</h4>
        <div className="grid grid-cols-2 gap-4">
          {/* Bids */}
          <div>
            <h5 className="text-sm font-semibold text-green-400 mb-2">Bids</h5>
            <div className="space-y-1">
              {data.market_depth.bids.slice(0, 10).map((bid, index) => (
                <div key={index} className="flex justify-between text-sm">
                  <span className="text-green-400">{bid[0].toFixed(2)}</span>
                  <span className="text-gray-300">{bid[1]}</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Asks */}
          <div>
            <h5 className="text-sm font-semibold text-red-400 mb-2">Asks</h5>
            <div className="space-y-1">
              {data.market_depth.asks.slice(0, 10).map((ask, index) => (
                <div key={index} className="flex justify-between text-sm">
                  <span className="text-red-400">{ask[0].toFixed(2)}</span>
                  <span className="text-gray-300">{ask[1]}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OffMarketVisualizer;
