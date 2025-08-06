#!/usr/bin/env python3
"""
Web-based fMRI Dashboard for Jupyter Hub
This version runs entirely within the Jupyter environment without external ports
"""
import os
import json
import time
import threading
from datetime import datetime
from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
from IPython.display import display, HTML

class DashboardData:
    """Simple data store for dashboard values"""
    def __init__(self):
        self.clf_data = None
        self.mc_data = None
        self.feedback_status = None
        self.run_number = None
        self.feedback_number = None
        self.last_update = None

# Global data store
dashboard_data = DashboardData()

def create_dashboard_widgets():
    """Create interactive dashboard widgets"""
    
    # Create output widgets
    clf_output = widgets.HTML(value="<div style='font-size: 2em; text-align: center;'>--</div>")
    run_output = widgets.HTML(value="<div style='font-size: 2em; text-align: center;'>--</div>")
    feedback_output = widgets.HTML(value="<div style='font-size: 2em; text-align: center;'>--</div>")
    mc_output = widgets.HTML(value="<div style='font-size: 1.2em; text-align: center;'>--</div>")
    status_output = widgets.HTML(value="<div style='font-size: 1.2em; text-align: center; color: gray;'>NEUROFEEDBACK NOT SENT</div>")
    timestamp_output = widgets.HTML(value="<div style='font-size: 0.8em; text-align: center; color: gray;'>No data received</div>")
    
    # Create test buttons
    test_clf_btn = widgets.Button(description="Test Classifier")
    test_run_btn = widgets.Button(description="Test Run Number")
    test_feedback_btn = widgets.Button(description="Test Feedback Number")
    test_mc_btn = widgets.Button(description="Test Motion Correction")
    test_status_btn = widgets.Button(description="Test Neurofeedback Status")
    
    # Button event handlers
    def on_test_clf(b):
        update_dashboard_data('clf_data', 0.75, 1)
        update_display()
    
    def on_test_run(b):
        update_dashboard_data('run_number', 3, 1)
        update_display()
    
    def on_test_feedback(b):
        update_dashboard_data('feedback_number', 12, 1)
        update_display()
    
    def on_test_mc(b):
        update_dashboard_data('mc_data', [0.001, -0.002, 0.003, 0.0001, -0.0002, 0.0003], 1)
        update_display()
    
    def on_test_status(b):
        update_dashboard_data('feedback_status', True, 1)
        update_display()
    
    test_clf_btn.on_click(on_test_clf)
    test_run_btn.on_click(on_test_run)
    test_feedback_btn.on_click(on_test_feedback)
    test_mc_btn.on_click(on_test_mc)
    test_status_btn.on_click(on_test_status)
    
    # Create layout
    header = widgets.HTML(value="<h1 style='text-align: center; color: #667eea;'>neuroloopy</h1><h3 style='text-align: center; color: #764ba2;'>fMRI Neurofeedback Dashboard</h3>")
    
    # Main dashboard grid
    dashboard_grid = widgets.GridBox(
        children=[
            widgets.VBox([
                widgets.HTML(value="<h3>Classifier Output</h3>"),
                clf_output,
                timestamp_output
            ]),
            widgets.VBox([
                widgets.HTML(value="<h3>Run Number</h3>"),
                run_output,
                timestamp_output
            ]),
            widgets.VBox([
                widgets.HTML(value="<h3>Feedback Number</h3>"),
                feedback_output,
                timestamp_output
            ]),
            widgets.VBox([
                widgets.HTML(value="<h3>Motion Correction</h3>"),
                mc_output,
                timestamp_output
            ])
        ],
        layout=widgets.Layout(
            grid_template_columns='repeat(2, 1fr)',
            grid_gap='10px',
            width='100%'
        )
    )
    
    # Status section
    status_section = widgets.VBox([
        widgets.HTML(value="<h3>Neurofeedback Status</h3>"),
        status_output,
        timestamp_output
    ])
    
    # Test controls
    test_controls = widgets.HBox([
        test_clf_btn, test_run_btn, test_feedback_btn, test_mc_btn, test_status_btn
    ])
    
    # Store widgets for updates
    dashboard_data.widgets = {
        'clf_output': clf_output,
        'run_output': run_output,
        'feedback_output': feedback_output,
        'mc_output': mc_output,
        'status_output': status_output,
        'timestamp_output': timestamp_output
    }
    
    return widgets.VBox([
        header,
        status_section,
        dashboard_grid,
        test_controls
    ])

def update_dashboard_data(data_type, value, rep):
    """Update dashboard data"""
    if data_type == 'clf_data':
        dashboard_data.clf_data = {'value': value, 'rep': rep, 'timestamp': datetime.now()}
    elif data_type == 'run_number':
        dashboard_data.run_number = {'value': value, 'rep': rep, 'timestamp': datetime.now()}
    elif data_type == 'feedback_number':
        dashboard_data.feedback_number = {'value': value, 'rep': rep, 'timestamp': datetime.now()}
    elif data_type == 'mc_data':
        dashboard_data.mc_data = {'params': value, 'rep': rep, 'timestamp': datetime.now()}
    elif data_type == 'feedback_status':
        dashboard_data.feedback_status = {'sent': value, 'rep': rep, 'timestamp': datetime.now()}
    
    dashboard_data.last_update = datetime.now()

def update_display():
    """Update the dashboard display"""
    if not hasattr(dashboard_data, 'widgets'):
        return
    
    widgets = dashboard_data.widgets
    
    # Update classifier output
    if dashboard_data.clf_data:
        value = dashboard_data.clf_data['value']
        widgets['clf_output'].value = f"<div style='font-size: 2em; text-align: center; color: #4CAF50;'>{value:.4f}</div>"
        widgets['timestamp_output'].value = f"<div style='font-size: 0.8em; text-align: center; color: gray;'>Updated: {dashboard_data.clf_data['timestamp'].strftime('%H:%M:%S')}</div>"
    
    # Update run number
    if dashboard_data.run_number:
        value = dashboard_data.run_number['value']
        widgets['run_output'].value = f"<div style='font-size: 2em; text-align: center; color: #2196F3;'>{value}</div>"
    
    # Update feedback number
    if dashboard_data.feedback_number:
        value = dashboard_data.feedback_number['value']
        widgets['feedback_output'].value = f"<div style='font-size: 2em; text-align: center; color: #FF9800;'>{value}</div>"
    
    # Update motion correction
    if dashboard_data.mc_data:
        params = dashboard_data.mc_data['params']
        mc_html = f"""
        <div style='font-size: 1.2em; text-align: center; color: #9C27B0;'>
            X: {params[0]:.4f} | Y: {params[1]:.4f} | Z: {params[2]:.4f}<br>
            RX: {params[3]:.4f} | RY: {params[4]:.4f} | RZ: {params[5]:.4f}
        </div>
        """
        widgets['mc_output'].value = mc_html
    
    # Update neurofeedback status
    if dashboard_data.feedback_status:
        sent = dashboard_data.feedback_status['sent']
        if sent:
            widgets['status_output'].value = "<div style='font-size: 1.2em; text-align: center; color: #4CAF50; background: rgba(76, 175, 80, 0.2); padding: 10px; border-radius: 5px;'>NEUROFEEDBACK SENT</div>"
        else:
            widgets['status_output'].value = "<div style='font-size: 1.2em; text-align: center; color: #9E9E9E; background: rgba(158, 158, 158, 0.2); padding: 10px; border-radius: 5px;'>NEUROFEEDBACK NOT SENT</div>"

def start_dashboard():
    """Start the web-based dashboard"""
    print("🚀 Starting fMRI Dashboard (Web-based version)")
    print("✅ No external ports required - runs entirely in Jupyter")
    print("📊 Dashboard will appear below")
    print("🧪 Use the test buttons to simulate data")
    
    # Create and display dashboard
    dashboard = create_dashboard_widgets()
    display(dashboard)
    
    # Display instructions
    instructions = """
    <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0;">
        <h4>📋 How to Use:</h4>
        <ul>
            <li><strong>Test Buttons:</strong> Click to simulate different types of data</li>
            <li><strong>Real Data:</strong> Use the Python functions below to send real data</li>
            <li><strong>Integration:</strong> Import dashboard_integration.py in your fMRI pipeline</li>
        </ul>
        
        <h4>🔧 Python Integration:</h4>
        <pre style="background: #e0e0e0; padding: 10px; border-radius: 3px;">
from dashboard_integration import *

# Send classifier output
post_dashboard_clf_outs(0.75, 1)

# Send motion correction parameters
post_dashboard_mc_params([0.001, -0.002, 0.003, 0.0001, -0.0002, 0.0003], 1)

# Send neurofeedback status
post_dashboard_feedback_status(True, 1)

# Send run and feedback numbers
post_dashboard_run_number(3, 1)
post_dashboard_feedback_number(12, 1)
        </pre>
    </div>
    """
    display(HTML(instructions))
    
    return dashboard

# Python integration functions for real data
def post_dashboard_clf_outs(value, rep):
    """Send classifier output to dashboard"""
    update_dashboard_data('clf_data', value, rep)
    update_display()
    print(f"✅ Sent classifier output: {value} (rep {rep})")

def post_dashboard_mc_params(params, rep):
    """Send motion correction parameters to dashboard"""
    update_dashboard_data('mc_data', params, rep)
    update_display()
    print(f"✅ Sent motion correction parameters: {params} (rep {rep})")

def post_dashboard_feedback_status(sent, rep):
    """Send neurofeedback status to dashboard"""
    update_dashboard_data('feedback_status', sent, rep)
    update_display()
    print(f"✅ Sent neurofeedback status: {'SENT' if sent else 'NOT SENT'} (rep {rep})")

def post_dashboard_run_number(value, rep):
    """Send run number to dashboard"""
    update_dashboard_data('run_number', value, rep)
    update_display()
    print(f"✅ Sent run number: {value} (rep {rep})")

def post_dashboard_feedback_number(value, rep):
    """Send feedback number to dashboard"""
    update_dashboard_data('feedback_number', value, rep)
    update_display()
    print(f"✅ Sent feedback number: {value} (rep {rep})")

if __name__ == "__main__":
    # Start the dashboard
    dashboard = start_dashboard() 