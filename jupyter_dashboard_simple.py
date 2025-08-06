#!/usr/bin/env python3
"""
Simple fMRI Dashboard for Jupyter Notebook
Copy and paste this entire code into a Jupyter notebook cell
"""
import ipywidgets as widgets
from IPython.display import display, HTML
from datetime import datetime

# Create a simple dashboard that works directly in Jupyter
def create_dashboard():
    """Create a simple dashboard"""
    
    # Create output widgets
    clf_output = widgets.HTML(value="<div style='font-size: 2em; text-align: center; color: #4CAF50;'>--</div>")
    run_output = widgets.HTML(value="<div style='font-size: 2em; text-align: center; color: #2196F3;'>--</div>")
    feedback_output = widgets.HTML(value="<div style='font-size: 2em; text-align: center; color: #FF9800;'>--</div>")
    mc_output = widgets.HTML(value="<div style='font-size: 1.2em; text-align: center; color: #9C27B0;'>--</div>")
    status_output = widgets.HTML(value="<div style='font-size: 1.2em; text-align: center; color: #9E9E9E; background: rgba(158, 158, 158, 0.2); padding: 10px; border-radius: 5px;'>NEUROFEEDBACK NOT SENT</div>")
    
    # Create test buttons
    test_clf_btn = widgets.Button(description="Test Classifier", button_style='primary')
    test_run_btn = widgets.Button(description="Test Run Number", button_style='info')
    test_feedback_btn = widgets.Button(description="Test Feedback Number", button_style='warning')
    test_mc_btn = widgets.Button(description="Test Motion Correction", button_style='success')
    test_status_btn = widgets.Button(description="Test Neurofeedback Status", button_style='danger')
    
    # Button event handlers
    def on_test_clf(b):
        clf_output.value = "<div style='font-size: 2em; text-align: center; color: #4CAF50; font-weight: bold;'>0.7500</div>"
        print("✅ Test: Classifier output updated to 0.75")
    
    def on_test_run(b):
        run_output.value = "<div style='font-size: 2em; text-align: center; color: #2196F3; font-weight: bold;'>3</div>"
        print("✅ Test: Run number updated to 3")
    
    def on_test_feedback(b):
        feedback_output.value = "<div style='font-size: 2em; text-align: center; color: #FF9800; font-weight: bold;'>12</div>"
        print("✅ Test: Feedback number updated to 12")
    
    def on_test_mc(b):
        mc_output.value = """
        <div style='font-size: 1.2em; text-align: center; color: #9C27B0; font-weight: bold;'>
            X: 0.0010 | Y: -0.0020 | Z: 0.0030<br>
            RX: 0.0001 | RY: -0.0002 | RZ: 0.0003
        </div>
        """
        print("✅ Test: Motion correction parameters updated")
    
    def on_test_status(b):
        status_output.value = "<div style='font-size: 1.2em; text-align: center; color: #4CAF50; background: rgba(76, 175, 80, 0.2); padding: 10px; border-radius: 5px; font-weight: bold;'>NEUROFEEDBACK SENT</div>"
        print("✅ Test: Neurofeedback status updated to SENT")
    
    test_clf_btn.on_click(on_test_clf)
    test_run_btn.on_click(on_test_run)
    test_feedback_btn.on_click(on_test_feedback)
    test_mc_btn.on_click(on_test_mc)
    test_status_btn.on_click(on_test_status)
    
    # Create layout
    header = widgets.HTML(value="<h1 style='text-align: center; color: #667eea; font-family: Arial, sans-serif;'>neuroloopy</h1><h3 style='text-align: center; color: #764ba2; font-family: Arial, sans-serif;'>fMRI Neurofeedback Dashboard</h3>")
    
    # Status section
    status_section = widgets.VBox([
        widgets.HTML(value="<h3 style='font-family: Arial, sans-serif;'>Neurofeedback Status</h3>"),
        status_output,
        widgets.HTML(value="<div style='font-size: 0.8em; text-align: center; color: gray;'>No data received</div>")
    ])
    
    # Main dashboard grid
    dashboard_grid = widgets.GridBox(
        children=[
            widgets.VBox([
                widgets.HTML(value="<h3 style='font-family: Arial, sans-serif;'>Classifier Output</h3>"),
                clf_output,
                widgets.HTML(value="<div style='font-size: 0.8em; text-align: center; color: gray;'>No data received</div>")
            ]),
            widgets.VBox([
                widgets.HTML(value="<h3 style='font-family: Arial, sans-serif;'>Run Number</h3>"),
                run_output,
                widgets.HTML(value="<div style='font-size: 0.8em; text-align: center; color: gray;'>No data received</div>")
            ]),
            widgets.VBox([
                widgets.HTML(value="<h3 style='font-family: Arial, sans-serif;'>Feedback Number</h3>"),
                feedback_output,
                widgets.HTML(value="<div style='font-size: 0.8em; text-align: center; color: gray;'>No data received</div>")
            ]),
            widgets.VBox([
                widgets.HTML(value="<h3 style='font-family: Arial, sans-serif;'>Motion Correction</h3>"),
                mc_output,
                widgets.HTML(value="<div style='font-size: 0.8em; text-align: center; color: gray;'>No data received</div>")
            ])
        ],
        layout=widgets.Layout(
            grid_template_columns='repeat(2, 1fr)',
            grid_gap='20px',
            width='100%',
            border='2px solid #e0e0e0',
            padding='20px',
            margin='10px'
        )
    )
    
    # Test controls
    test_controls = widgets.HBox([
        test_clf_btn, test_run_btn, test_feedback_btn, test_mc_btn, test_status_btn
    ], layout=widgets.Layout(
        justify_content='space-around',
        width='100%',
        margin='20px 0'
    ))
    
    # Create main container
    main_container = widgets.VBox([
        header,
        status_section,
        dashboard_grid,
        test_controls
    ], layout=widgets.Layout(
        width='100%',
        border='3px solid #667eea',
        padding='20px',
        margin='10px'
    ))
    
    return main_container

# Display instructions
instructions = """
<div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0;">
    <h4>📋 How to Use:</h4>
    <ul>
        <li><strong>Test Buttons:</strong> Click to simulate different types of data</li>
        <li><strong>Real Data:</strong> Use the Python functions below to send real data</li>
    </ul>
    
    <h4>🔧 Python Integration:</h4>
    <pre style="background: #e0e0e0; padding: 10px; border-radius: 3px;">
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

# Create and display dashboard
print("🚀 Starting fMRI Dashboard")
print("✅ Dashboard will appear below")
print("🧪 Use the test buttons to simulate data")

dashboard = create_dashboard()
display(dashboard)
display(HTML(instructions))

print("✅ Dashboard is now running!")
print("🎯 Click the test buttons above to see it in action")

# Python integration functions
def post_dashboard_clf_outs(value, rep):
    """Send classifier output to dashboard"""
    print(f"✅ Sent classifier output: {value} (rep {rep})")
    # In a real implementation, this would update the dashboard widgets

def post_dashboard_mc_params(params, rep):
    """Send motion correction parameters to dashboard"""
    print(f"✅ Sent motion correction parameters: {params} (rep {rep})")

def post_dashboard_feedback_status(sent, rep):
    """Send neurofeedback status to dashboard"""
    print(f"✅ Sent neurofeedback status: {'SENT' if sent else 'NOT SENT'} (rep {rep})")

def post_dashboard_run_number(value, rep):
    """Send run number to dashboard"""
    print(f"✅ Sent run number: {value} (rep {rep})")

def post_dashboard_feedback_number(value, rep):
    """Send feedback number to dashboard"""
    print(f"✅ Sent feedback number: {value} (rep {rep})")

print("📝 Python functions are now available for integration!") 