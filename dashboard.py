import requests
import json
import time
from typing import Union, List, Optional

# Configuration
DASHBOARD_BASE_URL = "http://localhost:5001"
DASHBOARD_CLF_URL = f"{DASHBOARD_BASE_URL}/clf_data"
DASHBOARD_MC_URL = f"{DASHBOARD_BASE_URL}/mc_data"
DASHBOARD_FEEDBACK_URL = f"{DASHBOARD_BASE_URL}/feedback_status"
DASHBOARD_HEALTH_URL = f"{DASHBOARD_BASE_URL}/health"

# Timeout for HTTP requests
REQUEST_TIMEOUT = 0.5  # seconds

def check_dashboard_connection() -> bool:
    """
    Check if the dashboard server is running and accessible.
    
    Returns:
        bool: True if dashboard is accessible, False otherwise
    """
    try:
        response = requests.get(DASHBOARD_HEALTH_URL, timeout=REQUEST_TIMEOUT)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def post_dashboard_clf_outs(clf_value: Union[float, int], rep: int, url: Optional[str] = None) -> bool:
    """
    Post classifier output to the dashboard.
    
    Args:
        clf_value: The classifier output value
        rep: The repetition/volume number
        url: Optional custom URL (defaults to dashboard clf URL)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if url is None:
        url = DASHBOARD_CLF_URL
    
    payload = {
        "value": float(clf_value),
        "rep": int(rep)
    }
    
    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            print(f"Classifier data sent to dashboard - Rep: {rep}, Value: {clf_value}")
            return True
        else:
            print(f"Failed to send classifier data - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error sending classifier data: {e}")
        return False

def post_dashboard_mc_params(mc_params: Union[List[float], List[int]], rep: int, url: Optional[str] = None) -> bool:
    """
    Post motion correction parameters to the dashboard.
    
    Args:
        mc_params: List of motion correction parameters (typically 6 values: 3 translations + 3 rotations)
        rep: The repetition/volume number
        url: Optional custom URL (defaults to dashboard mc URL)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if url is None:
        url = DASHBOARD_MC_URL
    
    # Ensure mc_params is a list of floats
    if hasattr(mc_params, 'tolist'):  # Handle numpy arrays
        mc_params = mc_params.tolist()
    
    payload = {
        "params": [float(p) for p in mc_params],
        "rep": int(rep)
    }
    
    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            print(f"✅ Motion correction data sent to dashboard - Rep: {rep}, Params: {mc_params}")
            return True
        else:
            print(f"❌ Failed to send motion correction data - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending motion correction data: {e}")
        return False

def test_dashboard_connection():
    """
    Test function to verify dashboard connectivity and send sample data.
    """
    print("Testing dashboard connection...")
    
    if check_dashboard_connection():
        print("Dashboard server is running and accessible")
        
        # Send test classifier data
        print("Sending test classifier data...")
        post_dashboard_clf_outs(0.75, 1)
        
        # Send test motion correction data
        print("Sending test motion correction data...")
        test_mc_params = [0.001, -0.002, 0.003, 0.0001, -0.0002, 0.0003]
        post_dashboard_mc_params(test_mc_params, 1)
        
        print("Dashboard test completed successfully!")
        print(f"Dashboard available at: {DASHBOARD_BASE_URL}")
        
    else:
        print("Dashboard server is not accessible")
        print(f"Make sure the dashboard server is running at: {DASHBOARD_BASE_URL}")
        print("Start the server with: node server.js")

if __name__ == "__main__":
    test_dashboard_connection() 