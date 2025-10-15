@echo off
echo 🚀 Starting Order Flow Visualizer Frontend...
echo 📍 Frontend directory: %cd%\frontend
echo 🌐 Frontend URL: http://localhost:3000
echo ==================================================

cd frontend

echo 📦 Installing dependencies...
call npm install

echo 🎨 Starting React development server...
call npm start

pause
