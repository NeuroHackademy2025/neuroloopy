#!/usr/bin/env python3
"""
Jupyter Hub compatible launcher for the fMRI Real-time Dashboard
"""
import os
import subprocess
import sys
import time
import requests
import threading
from IPython.display import display, HTML

def check_port_availability(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def find_available_port(start_port=5001, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if not check_port_availability(port):
            return port
    return None

def start_server_with_port(port):
    """Start the server on a specific port"""
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'src', 'neuroloopy', 'dashboard')
    
    # Set the port environment variable
    env = os.environ.copy()
    env['PORT'] = str(port)
    
    # Start the server
    process = subprocess.Popen(
        ['node', 'server.js'], 
        cwd=dashboard_dir, 
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    return process

def wait_for_server(port, timeout=30):
    """Wait for server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f'http://localhost:{port}/health', timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    """Start the dashboard server with Jupyter Hub compatibility"""
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'src', 'neuroloopy', 'dashboard')
    
    if not os.path.exists(dashboard_dir):
        print(f"Error: Dashboard directory not found at {dashboard_dir}")
        return
    
    # Check if node_modules exists, if not install dependencies
    node_modules_path = os.path.join(dashboard_dir, 'node_modules')
    if not os.path.exists(node_modules_path):
        print("Installing Node.js dependencies...")
        subprocess.run(['npm', 'install'], cwd=dashboard_dir, check=True)
    
    # Find available port
    port = find_available_port()
    if port is None:
        print("Error: No available ports found")
        return
    
    print(f"Starting fMRI Real-time Dashboard on port {port}...")
    print(f"Dashboard will be available at: http://localhost:{port}")
    
    # Start server
    process = start_server_with_port(port)
    
    # Wait for server to be ready
    print("Waiting for server to start...")
    if wait_for_server(port):
        print(f"✅ Server is running at http://localhost:{port}")
        
        # Create clickable link for Jupyter
        dashboard_url = f"http://localhost:{port}"
        html_content = f"""
        <div style="padding: 10px; background: #f0f0f0; border-radius: 5px; margin: 10px 0;">
            <h3>🎯 fMRI Dashboard is Running!</h3>
            <p><strong>Dashboard URL:</strong> <a href="{dashboard_url}" target="_blank">{dashboard_url}</a></p>
            <p><strong>Health Check:</strong> <a href="{dashboard_url}/health" target="_blank">{dashboard_url}/health</a></p>
            <p><em>Click the links above to open the dashboard in a new tab</em></p>
        </div>
        """
        display(HTML(html_content))
        
        # Keep the process alive
        try:
            while True:
                time.sleep(1)
                if process.poll() is not None:
                    print(f"Server process exited with code: {process.returncode}")
                    break
        except KeyboardInterrupt:
            print("\nStopping server...")
            process.terminate()
            process.wait()
            print("Server stopped")
    else:
        print("❌ Server failed to start within timeout")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main() 