#!/usr/bin/env python3
"""
Diagnostic script for the fMRI Real-time Dashboard
"""
import os
import sys
import subprocess
import requests
import time

def check_python_version():
    """Check if Python version is compatible"""
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 6):
        print("Warning: Python 3.6+ is recommended")
    else:
        print("✓ Python version is compatible")

def check_node_installation():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Node.js version: {result.stdout.strip()}")
            return True
        else:
            print("✗ Node.js not found")
            return False
    except FileNotFoundError:
        print("✗ Node.js not found. Please install Node.js from https://nodejs.org/")
        return False

def check_npm_installation():
    """Check if npm is installed"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ npm version: {result.stdout.strip()}")
            return True
        else:
            print("✗ npm not found")
            return False
    except FileNotFoundError:
        print("✗ npm not found. Please install npm")
        return False

def check_dashboard_files():
    """Check if all dashboard files exist"""
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'src', 'neuroloopy', 'dashboard')
    
    required_files = [
        'dashboard.html',
        'server.js', 
        'dashboard.py',
        'package.json'
    ]
    
    print(f"\nChecking dashboard files in: {dashboard_dir}")
    
    if not os.path.exists(dashboard_dir):
        print("✗ Dashboard directory not found")
        return False
    
    all_files_exist = True
    for file in required_files:
        file_path = os.path.join(dashboard_dir, file)
        if os.path.exists(file_path):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            all_files_exist = False
    
    return all_files_exist

def check_dependencies():
    """Check if Node.js dependencies are installed"""
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'src', 'neuroloopy', 'dashboard')
    node_modules_path = os.path.join(dashboard_dir, 'node_modules')
    
    if os.path.exists(node_modules_path):
        print("✓ Node.js dependencies installed")
        return True
    else:
        print("✗ Node.js dependencies not installed")
        print("  Run: python3 start_dashboard.py")
        return False

def test_server_connection():
    """Test if the server can be started and accessed"""
    print("\nTesting server connection...")
    
    # Start server in background
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'src', 'neuroloopy', 'dashboard')
    
    try:
        # Start server
        process = subprocess.Popen(['node', 'server.js'], cwd=dashboard_dir)
        
        # Wait for server to start
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:5001/health', timeout=5)
            if response.status_code == 200:
                print("✓ Server is running and responding")
                print(f"  Health response: {response.json()}")
            else:
                print(f"✗ Server responded with status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Could not connect to server: {e}")
        
        # Test dashboard page
        try:
            response = requests.get('http://localhost:5001/', timeout=5)
            if response.status_code == 200:
                print("✓ Dashboard page is accessible")
            else:
                print(f"✗ Dashboard page returned status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Could not access dashboard page: {e}")
        
        # Stop server
        process.terminate()
        process.wait()
        
    except Exception as e:
        print(f"✗ Error testing server: {e}")

def main():
    """Run all diagnostic checks"""
    print("=== fMRI Dashboard Diagnostic Tool ===\n")
    
    check_python_version()
    print()
    
    node_ok = check_node_installation()
    npm_ok = check_npm_installation()
    print()
    
    files_ok = check_dashboard_files()
    print()
    
    deps_ok = check_dependencies()
    print()
    
    if node_ok and npm_ok and files_ok and deps_ok:
        print("All checks passed! Testing server...")
        test_server_connection()
    else:
        print("Some checks failed. Please fix the issues above before running the dashboard.")
        print("\nTroubleshooting steps:")
        print("1. Install Node.js from https://nodejs.org/")
        print("2. Make sure you're on the dashboard-feature branch: git checkout dashboard-feature")
        print("3. Run: python3 start_dashboard.py")
        print("4. Open http://localhost:5001 in your browser")

if __name__ == "__main__":
    main() 