#!/bin/bash

echo "🚀 Setting up fMRI Dashboard..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first:"
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm are installed"

# Navigate to dashboard directory
cd src/neuroloopy/dashboard

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Start the server
echo "🚀 Starting dashboard server..."
echo "📊 Dashboard will be available at: http://localhost:8080"
echo "🌐 For network access, use your IP address: http://YOUR_IP:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm start 