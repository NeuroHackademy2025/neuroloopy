#!/usr/bin/env python3
"""
Simple test to start the dashboard server and keep it running
"""
import os
import subprocess
import time
import signal
import sys

def main():
    """Start the server and keep it running"""
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'src', 'neuroloopy', 'dashboard')
    
    print(f"Starting server from: {dashboard_dir}")
    print("Server will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop")
    
    try:
        # Start the server process
        process = subprocess.Popen(['node', 'server.js'], cwd=dashboard_dir)
        
        print(f"Server started with PID: {process.pid}")
        
        # Keep the script running
        while True:
            time.sleep(1)
            # Check if process is still running
            if process.poll() is not None:
                print(f"Server process exited with code: {process.returncode}")
                break
                
    except KeyboardInterrupt:
        print("\nStopping server...")
        if 'process' in locals():
            process.terminate()
            process.wait()
        print("Server stopped")

if __name__ == "__main__":
    main() 