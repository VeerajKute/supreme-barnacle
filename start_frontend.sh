#!/bin/bash

echo "🚀 Starting Order Flow Visualizer Frontend..."
echo "📍 Frontend directory: $(pwd)/frontend"
echo "🌐 Frontend URL: http://localhost:3000"
echo "=================================================="

cd frontend

echo "📦 Installing dependencies..."
npm install

echo "🎨 Starting React development server..."
npm start
