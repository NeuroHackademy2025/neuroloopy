"""
Dashboard integration functions for neuroloopy.
"""

import requests
import time


def post_dashboard_clf_outs(clf_out, rep, dashboard_url):
    """
    Post classifier outputs to dashboard.
    
    Args:
        clf_out: Classifier output
        rep: Repetition number
        dashboard_url: Dashboard URL
    """
    try:
        payload = {
            "value": float(clf_out),
            "rep": int(rep)
        }
        response = requests.post(dashboard_url, json=payload, timeout=1.0)
        if response.status_code == 200:
            print(f"Dashboard: Posted classifier output for rep {rep}")
        else:
            print(f"Dashboard: Failed to post classifier output (status: {response.status_code})")
    except Exception as e:
        print(f"Dashboard: Error posting classifier output: {e}")


def post_dashboard_mc_params(mc_params, rep, dashboard_url):
    """
    Post motion correction parameters to dashboard.
    
    Args:
        mc_params: Motion correction parameters
        rep: Repetition number
        dashboard_url: Dashboard URL
    """
    try:
        payload = {
            "params": mc_params.tolist() if hasattr(mc_params, 'tolist') else list(mc_params),
            "rep": int(rep)
        }
        response = requests.post(dashboard_url, json=payload, timeout=1.0)
        if response.status_code == 200:
            print(f"Dashboard: Posted motion correction params for rep {rep}")
        else:
            print(f"Dashboard: Failed to post motion correction params (status: {response.status_code})")
    except Exception as e:
        print(f"Dashboard: Error posting motion correction params: {e}")


def post_dashboard_feedback_status(sent, rep, dashboard_url):
    """
    Post feedback status to dashboard.
    
    Args:
        sent: Whether feedback was sent
        rep: Repetition number
        dashboard_url: Dashboard URL
    """
    try:
        payload = {
            "sent": bool(sent),
            "rep": int(rep)
        }
        response = requests.post(dashboard_url, json=payload, timeout=1.0)
        if response.status_code == 200:
            print(f"Dashboard: Posted feedback status for rep {rep}")
        else:
            print(f"Dashboard: Failed to post feedback status (status: {response.status_code})")
    except Exception as e:
        print(f"Dashboard: Error posting feedback status: {e}")


def post_dashboard_run_number(run_number, rep, dashboard_url):
    """
    Post run number to dashboard.
    
    Args:
        run_number: Current run number
        rep: Repetition number
        dashboard_url: Dashboard URL
    """
    try:
        payload = {
            "value": int(run_number),
            "rep": int(rep)
        }
        response = requests.post(dashboard_url, json=payload, timeout=1.0)
        if response.status_code == 200:
            print(f"Dashboard: Posted run number for rep {rep}")
        else:
            print(f"Dashboard: Failed to post run number (status: {response.status_code})")
    except Exception as e:
        print(f"Dashboard: Error posting run number: {e}")


def post_dashboard_feedback_number(feedback_number, rep, dashboard_url):
    """
    Post feedback number to dashboard.
    
    Args:
        feedback_number: Current feedback number
        rep: Repetition number
        dashboard_url: Dashboard URL
    """
    try:
        payload = {
            "value": int(feedback_number),
            "rep": int(rep)
        }
        response = requests.post(dashboard_url, json=payload, timeout=1.0)
        if response.status_code == 200:
            print(f"Dashboard: Posted feedback number for rep {rep}")
        else:
            print(f"Dashboard: Failed to post feedback number (status: {response.status_code})")
    except Exception as e:
        print(f"Dashboard: Error posting feedback number: {e}")


def check_dashboard_health(dashboard_url):
    """
    Check dashboard health.
    
    Args:
        dashboard_url: Dashboard base URL
    
    Returns:
        bool: True if dashboard is healthy, False otherwise
    """
    try:
        health_url = dashboard_url.rstrip('/') + '/health'
        response = requests.get(health_url, timeout=2.0)
        if response.status_code == 200:
            data = response.json()
            return data.get('status') == 'ok'
        else:
            return False
    except Exception as e:
        print(f"Dashboard: Health check failed: {e}")
        return False 