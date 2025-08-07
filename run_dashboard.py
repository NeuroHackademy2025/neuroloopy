#!/usr/bin/env python3
"""
Simple launcher for the fMRI Real-time Dashboard
"""
import os
import subprocess
import sys

def main():
    """Start the dashboard server"""
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'src', 'neuroloopy', 'dashboard')
    
    if not os.path.exists(dashboard_dir):
        print(f"Error: Dashboard directory not found at {dashboard_dir}")
        sys.exit(1)
    
    # Check if node_modules exists, if not install dependencies
    node_modules_path = os.path.join(dashboard_dir, 'node_modules')
    if not os.path.exists(node_modules_path):
        print("Installing Node.js dependencies...")
        subprocess.run(['npm', 'install'], cwd=dashboard_dir, check=True)
    
    print("Starting fMRI Real-time Dashboard...")
    print(f"Dashboard will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    # Change to dashboard directory and start server
    os.chdir(dashboard_dir)
    subprocess.run(['node', 'server.js'])

if __name__ == "__main__":
    main() 