# Jupyter Hub Dashboard Setup Guide

## 🎯 Overview

This guide helps you run the fMRI dashboard in Jupyter Hub environments, which have different networking and process management constraints.

## 🚀 Quick Start

### Option 1: Jupyter Notebook (Recommended)
1. Open `dashboard_jupyter.ipynb` in your Jupyter environment
2. Run all cells in order
3. Click the generated links to access the dashboard

### Option 2: Python Script
```bash
python3 jupyter_dashboard.py
```

## 🔧 Jupyter Hub Specific Issues

### 1. Port Access Issues
**Problem**: Jupyter Hub may block certain ports
**Solution**: The launcher automatically finds available ports

### 2. Process Management
**Problem**: Jupyter Hub may kill long-running processes
**Solution**: Use the notebook version which keeps the process alive

### 3. Network Isolation
**Problem**: Server not accessible from browser
**Solution**: Use `localhost` URLs provided by the launcher

### 4. File System Permissions
**Problem**: Cannot install dependencies or access files
**Solution**: Check file permissions and use the diagnostic tool

## 📋 Step-by-Step Instructions

### 1. Clone and Setup
```bash
git clone https://github.com/NeuroHackademy2025/neuroloopy.git
cd neuroloopy
git checkout dashboard-feature
```

### 2. Run Diagnostic Tool
```bash
python3 test_dashboard.py
```

### 3. Start Dashboard (Choose One)

#### Option A: Jupyter Notebook
```bash
jupyter notebook dashboard_jupyter.ipynb
```

#### Option B: Python Script
```bash
python3 jupyter_dashboard.py
```

#### Option C: Direct Node.js
```bash
cd src/neuroloopy/dashboard
PORT=5001 node server.js
```

### 4. Access Dashboard
- Click the generated links in the notebook
- Or open `http://localhost:[PORT]` in your browser
- Replace `[PORT]` with the actual port number shown

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
lsof -i :5001

# Kill the process
kill [PID]

# Or use a different port
PORT=5002 node server.js
```

### Node.js Not Found
```bash
# Install Node.js in Jupyter environment
conda install nodejs
# or
pip install nodejs
```

### Dependencies Missing
```bash
cd src/neuroloopy/dashboard
npm install
```

### Permission Denied
```bash
# Check file permissions
ls -la src/neuroloopy/dashboard/

# Make files executable
chmod +x jupyter_dashboard.py
```

## 🎯 Expected Output

When successful, you should see:
```
✅ Dashboard directory found at /path/to/src/neuroloopy/dashboard
✅ Dependencies already installed
✅ Found available port: 5001
🚀 Starting server on port 5001...
⏳ Waiting for server to start...
✅ Server is running at http://localhost:5001
```

And a clickable link in the notebook:
```
🎯 fMRI Dashboard is Running!
Dashboard URL: http://localhost:5001
Health Check: http://localhost:5001/health
```

## 🛑 Stopping the Server

### In Jupyter Notebook
Run the "Stop Server" cell

### In Terminal
Press `Ctrl+C` or run:
```bash
pkill -f "node server.js"
```

## 📞 Getting Help

If you're still having issues:
1. Run `python3 test_dashboard.py` and share the output
2. Check the Jupyter Hub logs for any error messages
3. Try using a different port (5002, 5003, etc.)
4. Make sure you're on the `dashboard-feature` branch

## 🔗 Useful Links

- **Repository**: https://github.com/NeuroHackademy2025/neuroloopy
- **Branch**: `dashboard-feature`
- **Main Guide**: `TROUBLESHOOTING.md`
- **Diagnostic Tool**: `test_dashboard.py` 