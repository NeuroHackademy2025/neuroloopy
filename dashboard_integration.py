#!/usr/bin/env python3
"""
Dashboard integration module for fMRI real-time monitoring
This module provides functions to send data to the dashboard server.
"""

import sys
import os

# Add the dashboard directory to the path
dashboard_dir = os.path.join(os.path.dirname(__file__), 'src', 'neuroloopy', 'dashboard')
sys.path.insert(0, dashboard_dir)

# Import the dashboard functions
from dashboard import (
    post_dashboard_clf_outs,
    post_dashboard_mc_params,
    post_dashboard_feedback_status,
    post_dashboard_run_number,
    post_dashboard_feedback_number,
    check_dashboard_connection,
    test_dashboard_connection
)

# Re-export the functions for easy access
__all__ = [
    'post_dashboard_clf_outs',
    'post_dashboard_mc_params', 
    'post_dashboard_feedback_status',
    'post_dashboard_run_number',
    'post_dashboard_feedback_number',
    'check_dashboard_connection',
    'test_dashboard_connection'
]

if __name__ == "__main__":
    # Run the test function
    test_dashboard_connection() 