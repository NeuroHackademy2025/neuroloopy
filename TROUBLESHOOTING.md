# fMRI Dashboard Troubleshooting Guide

## Common Issues and Solutions

### 1. "Cannot find module" or "Module not found" errors

**Problem**: Node.js can't find the server.js file
**Solution**: Make sure you're running the commands from the correct directory

```bash
# Make sure you're in the neuroloopy root directory
cd neuroloopy

# Check if you're on the right branch
git checkout dashboard-feature

# Use the launcher script (recommended)
python3 start_dashboard.py

# OR manually navigate to the dashboard directory
cd src/neuroloopy/dashboard
node server.js
```

### 2. "Port already in use" error

**Problem**: Port 5001 is already being used by another process
**Solution**: Kill existing processes or use a different port

```bash
# Find what's using port 5001
lsof -i :5001

# Kill the process (replace PID with the actual process ID)
kill <PID>

# Or use a different port by editing server.js
```

### 3. "Node.js not found" error

**Problem**: Node.js is not installed
**Solution**: Install Node.js

```bash
# On macOS with Homebrew
brew install node

# On Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# On Windows
# Download from https://nodejs.org/
```

### 4. "npm not found" error

**Problem**: npm is not installed
**Solution**: Install npm (usually comes with Node.js)

```bash
# On macOS
brew install node  # This includes npm

# On Ubuntu/Debian
sudo apt install npm
```

### 5. Dashboard page doesn't load

**Problem**: Server is running but page won't load
**Solution**: Check browser and server

```bash
# Test if server is responding
curl http://localhost:5001/health

# Check if dashboard page loads
curl http://localhost:5001/

# Try different browser or incognito mode
# Clear browser cache
```

### 6. "Dependencies not installed" error

**Problem**: Node.js packages are missing
**Solution**: Install dependencies

```bash
# Navigate to dashboard directory
cd src/neuroloopy/dashboard

# Install dependencies
npm install

# Or use the launcher script which does this automatically
python3 start_dashboard.py
```

### 7. "Permission denied" errors

**Problem**: Insufficient permissions
**Solution**: Check file permissions

```bash
# Make sure files are executable
chmod +x start_dashboard.py
chmod +x test_dashboard.py

# On Windows, run as administrator if needed
```

## Diagnostic Tool

Run the diagnostic tool to automatically check for common issues:

```bash
python3 test_dashboard.py
```

This will check:
- Python version
- Node.js installation
- npm installation
- Dashboard files existence
- Dependencies installation
- Server connectivity

## Step-by-Step Setup for Teammates

1. **Clone the repository**:
   ```bash
   git clone https://github.com/NeuroHackademy2025/neuroloopy.git
   cd neuroloopy
   ```

2. **Checkout the dashboard branch**:
   ```bash
   git checkout dashboard-feature
   ```

3. **Install Node.js** (if not already installed):
   ```bash
   # macOS
   brew install node
   
   # Ubuntu/Debian
   sudo apt update && sudo apt install nodejs npm
   ```

4. **Run the diagnostic tool**:
   ```bash
   python3 test_dashboard.py
   ```

5. **Start the dashboard**:
   ```bash
   python3 start_dashboard.py
   ```

6. **Open in browser**:
   ```
   http://localhost:5001
   ```

## File Structure

Make sure your directory structure looks like this:

```
neuroloopy/
├── src/neuroloopy/dashboard/
│   ├── dashboard.html
│   ├── server.js
│   ├── dashboard.py
│   ├── package.json
│   └── node_modules/
├── start_dashboard.py
├── dashboard_integration.py
├── test_dashboard.py
└── TROUBLESHOOTING.md
```

## Still Having Issues?

1. Run the diagnostic tool: `python3 test_dashboard.py`
2. Check the console output for error messages
3. Make sure you're on the `dashboard-feature` branch
4. Try clearing browser cache and cookies
5. Check if any firewall is blocking localhost connections
6. Try a different browser or incognito mode

## Getting Help

If you're still having issues:
1. Run `python3 test_dashboard.py` and share the output
2. Check the browser's developer console for JavaScript errors
3. Share any error messages from the terminal 