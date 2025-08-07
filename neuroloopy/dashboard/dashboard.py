import requests
import json
import time
from typing import Union, List, Optional

# Configuration
DASHBOARD_BASE_URL = "http://localhost:5001"
DASHBOARD_CLF_URL = f"{DASHBOARD_BASE_URL}/clf_data"
DASHBOARD_MC_URL = f"{DASHBOARD_BASE_URL}/mc_data"
DASHBOARD_FEEDBACK_URL = f"{DASHBOARD_BASE_URL}/feedback_status"
DASHBOARD_RUN_NUMBER_URL = f"{DASHBOARD_BASE_URL}/run_number"
DASHBOARD_FEEDBACK_NUMBER_URL = f"{DASHBOARD_BASE_URL}/feedback_number"
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

def post_dashboard_feedback_status(sent, rep, url=None):
    """
    Send neurofeedback delivery status to the dashboard.
    
    Args:
        sent (bool): Whether neurofeedback was sent to participant
        rep (int): Repetition/volume number
        url (str, optional): Custom endpoint URL
    
    Returns:
        bool: True if successful, False otherwise
    """
    if url is None:
        url = DASHBOARD_FEEDBACK_URL
    
    payload = {"sent": bool(sent), "rep": int(rep)}
    response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    return response.status_code == 200

def post_dashboard_run_number(run_number, rep, url=None):
    """
    Send run number to the dashboard.
    
    Args:
        run_number (int): Current run number
        rep (int): Repetition/volume number
        url (str, optional): Custom endpoint URL
    
    Returns:
        bool: True if successful, False otherwise
    """
    if url is None:
        url = DASHBOARD_RUN_NUMBER_URL
    
    payload = {"value": int(run_number), "rep": int(rep)}
    response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    return response.status_code == 200

def post_dashboard_feedback_number(feedback_number, rep, url=None):
    """
    Send feedback number to the dashboard.
    
    Args:
        feedback_number (int): Current feedback number
        rep (int): Repetition/volume number
        url (str, optional): Custom endpoint URL
    
    Returns:
        bool: True if successful, False otherwise
    """
    if url is None:
        url = DASHBOARD_FEEDBACK_NUMBER_URL
    
    payload = {"value": int(feedback_number), "rep": int(rep)}
    response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    return response.status_code == 200

def test_dashboard_connection():
    """
    Test the dashboard connection and send sample data.
    """
    print("Testing dashboard connection...")
    
    # Check if server is running
    if not check_dashboard_connection():
        print("Dashboard server is not accessible. Make sure it's running on http://localhost:5001")
        return False
    
    print("Dashboard server is accessible!")
    
    # Send sample data
    print("Sending sample data...")
    
    # Sample classifier data
    success1 = post_dashboard_clf_outs(0.75, 1)
    print(f"Classifier data: {'Success' if success1 else 'Failed'}")
    
    # Sample motion correction data
    mc_params = [0.001, -0.002, 0.003, 0.0001, -0.0002, 0.0003]
    success2 = post_dashboard_mc_params(mc_params, 1)
    print(f"Motion correction data: {'Success' if success2 else 'Failed'}")
    
    # Sample neurofeedback status
    success3 = post_dashboard_feedback_status(True, 1)
    print(f"Neurofeedback status: {'Success' if success3 else 'Failed'}")
    
    # Sample run number
    success4 = post_dashboard_run_number(3, 1)
    print(f"Run number: {'Success' if success4 else 'Failed'}")
    
    # Sample feedback number
    success5 = post_dashboard_feedback_number(12, 1)
    print(f"Feedback number: {'Success' if success5 else 'Failed'}")
    
    print("Test completed!")
    return True

if __name__ == "__main__":
    test_dashboard_connection() 