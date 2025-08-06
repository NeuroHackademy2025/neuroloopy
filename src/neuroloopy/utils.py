# utils functions for neuroloopy
import nibabel as nib
import numpy as np
import os, glob, yaml
import pickle as pkl
import requests as r

def generate_config_template(output_path="config_template.yaml"):
    """
    Generates a template YAML configuration file with all required parameters.
    
    Args:
        output_path (str): Path where the template file should be saved
    """

    # Create the YAML content with comments
    yaml_content = """# Configuration Template for Real-time fMRI Processing
# Fill in the values below according to your experimental setup

# ==============================================================================
# BASIC RUN CONFIGURATION
# ==============================================================================

# Starting run number (will be decremented by 1 for run_count)
start_run: 1

# Feedback mode: 'continuous' or 'intermittent'
feedback_mode: "continuous"

# ==============================================================================
# TIMING PARAMETERS (in TRs)
# ==============================================================================

# Baseline period at start of run
baseline_trs: 10

# Number of TRs for feedback period
feedback_trs: 20

# For intermittent feedback mode only:
encoding_trs: 4      # TRs during encoding period
cue_trs: 2           # TRs during cue presentation
wait_trs: 6          # TRs during waiting period
iti_trs: 4           # Inter-trial interval TRs
trials: 8            # Number of trials per run
runEnd_fix_trs: 10   # Fixation TRs at end of run

# ==============================================================================
# DIRECTORY PATHS
# ==============================================================================

# Directory where real-time data will appear
watch_dir: "/path/to/realtime/data"

# Reference directory containing warp files
ref_dir: "/path/to/reference/files"

# Reference director to dcm2niix binary
dcm2niix_dir: "/path/to/dcm2niix"

# Archive settings
archive_data: true
archive_dir: "/path/to/archive/directory"
"""
    
    with open(output_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"Configuration template saved to: {output_path}")
    return output_path

def setup_config(config_path):
    """
    Reads a YAML configuration file and returns the configuration as a dictionary.
    Args:
        config_path (str): Path to the YAML configuration file.
    Returns:
        dict: Configuration parameters.
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # setup values from config
    config['run_count'] = int(config['start_run'])-1
    config['feedback_mode'] = config['feedback_mode'].lower()
    config['run_trs'] = config['baseline_trs']+config['feedback_trs']
    
    if config['feedback_mode'] == 'continuous':
        config['run_trs'] = config['baseline_trs']+config['feedback_trs']
        config['feedback_calc_trs'] = np.arange(config['baseline_trs'],config['feedback_trs']+config['baseline_trs'])
    elif config['feedback_mode'] == 'intermittent': 
        config['trial_trs'] = config['encoding_trs']+config['cue_trs']+config['wait_trs']+config['feedback_trs']+config['iti_trs']
        config['run_trs'] = (config['baseline_trs']+config['trials']*config['trial_trs'])+config['runEnd_fix_trs']
        config['trs_to_score_calc'] = config['cue_trs']+config['wait_trs']
        config['feedback_calc_trs'] = (config['baseline_trs']+config['trs_to_score_calc']+np.arange(config['trials'])*config['trial_trs']-1)
   
    config['warp_file'] = glob.glob(config['ref_dir']+'/*warp_displacement.nii.gz')[0] # only if mni conversion
    # config['standard_dir'] = os.getcwd()+'/standard'
    # alinging it to mni brain - all things that would only be called if you set in the config file
    # config['mni_template'] = glob.glob(config['standard_dir']+'/*2mm_brain.nii.gz')[0]
    # as the processesing happens the processing directory is where the conversion is happening and then it gets deleted
    config['proc_dir'] = os.getcwd()+'/proc' 
    config['REALTIME_TIMEOUT'] = 0.1  # seconds for real-time requests
    return config

def validate_config(config_path):
    """
    Validates that a configuration file contains all required parameters.
    
    Args:
        config_path (str): Path to the configuration file to validate
        
    Returns:
        tuple: (is_valid, missing_params, validation_messages)
    """
    required_params = {
        'basic': ['start_run', 'feedback_mode', 'baseline_trs', 'feedback_trs'],
        'paths': ['watch_dir', 'ref_dir', 'archive_data', 'archive_dir'],
        'intermittent_only': ['encoding_trs', 'cue_trs', 'wait_trs', 'iti_trs', 'trials', 'runEnd_fix_trs']
    }
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        return False, [], [f"Error reading config file: {e}"]
    
    missing_params = []
    validation_messages = []
    
    # Check basic required parameters
    for param in required_params['basic'] + required_params['paths']:
        if param not in config:
            missing_params.append(param)
    
    # Check intermittent-specific parameters if needed
    if config.get('feedback-mode', '').lower() == 'intermittent':
        for param in required_params['intermittent_only']:
            if param not in config:
                missing_params.append(param)
    
    # Validate feedback mode
    if 'feedback_mode' in config:
        if config['feedback_mode'].lower() not in ['continuous', 'intermittent']:
            validation_messages.append("feedback-mode must be 'continuous' or 'intermittent'")
    
    # Check if paths exist (for directories that should exist)
    path_checks = ['ref_dir']  # watch-dir might not exist yet, archive-dir might be created
    for path_param in path_checks:
        if path_param in config and not os.path.exists(config[path_param]):
            validation_messages.append(f"Path does not exist: {config[path_param]} (for {path_param})")
    
    is_valid = len(missing_params) == 0 and len(validation_messages) == 0
    
    if missing_params:
        validation_messages.append(f"Missing required parameters: {', '.join(missing_params)}")
    
    return is_valid, missing_params, validation_messages

def send_loop_output(payload, config=config):
    print('payload:', payload)  # dw
    try:
        r.post(config['post_url'], json=payload, timeout=config['REALTIME_TIMEOUT'])
        # dw: how to print out the current url?
    except:
        pass
#     # return: feedback number, array w/ classifier output, not cumulative (new file for each rep)
# def read_loop_output