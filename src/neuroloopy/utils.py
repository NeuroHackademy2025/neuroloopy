# utils functions for neuroloopy
import numpy as np
import os, glob, yaml, sys, time
import pickle as pkl
import requests as r

def generate_config_template(output_path="config_template.yaml"):
    """
    Generates a template YAML configuration file with all required parameters.
    Args:
        output_path (str): Path where the template file should be saved
    """
    template_config = {
        # Metadata
        'experiment_name': 'neuroloopy_experiment',
        'mc_mode': 'afni',
        'predict_type': 'prob_est',
        # Connection settings
        'post_url': 'http://localhost:5000/api/feedback',
        'dashboard-base-url': 'http://localhost:3000',  # optional, only if using a dashboard
        # Basic run configuration
        'script_start_time': None,
        'start_run': 1,
        'feedback_mode': 'continuous',  # or 'intermittent'
        # Timing parameters (in TRs)
        'baseline_trs': 10,
        'feedback_trs': 20,
        'moving_avg_trs': 5,
        # For intermittent mode only
        'encoding_trs': 4,
        'cue_trs': 2,
        'wait_trs': 6,
        'iti_trs': 4,
        'trials': 8,
        'runEnd_fix_trs': 10,
        # Directory & file paths
        'watch_dir': '/path/to/realtime/data',
        'model_dir': '/path/to/model/files',
        'dcm2niix_dir': '/path/to/dcm2niix',
        # Optional logging/debugging
        'archive_dir': '/path/to/archive/directory',
        'log_dir': None,
        # Optionally defined directories (otherwise assumed to be subject or current working directory)
        'ref_dir': '/path/to/reference/files',
        'mni_template': '/path/to/mni/template.nii.gz',
    }

    # Create the YAML content with comments
    yaml_content = """# Configuration Template for Real-time fMRI Processing
# Fill in the values below according to your experimental setup

# ==============================================================================
# METADATA
# ==============================================================================
# Name of the experiment
experiment_name: "neuroloopy_experiment"

# Motion correction mode
mc_mode: "afni"

# ==============================================================================
# CONNECTION SETTINGS
# ==============================================================================
# URL for posting feedback data
post_url: "http://localhost:5000/api/feedback"

# Dashboard base URL (optional, only if using a dashboard)
dashboard-base-url: "http://localhost:3000"

# ==============================================================================
# BASIC RUN CONFIGURATION
# ==============================================================================
# Script start time (will be set at runtime)
script_start_time: null

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

# Number of TRs for moving average calculation
moving_avg_trs: 5

# For intermittent feedback mode only:
encoding_trs: 4      # TRs during encoding period
cue_trs: 2           # TRs during cue presentation
wait_trs: 6          # TRs during waiting period
iti_trs: 4           # Inter-trial interval TRs
trials: 8            # Number of trials per run
runEnd_fix_trs: 10   # Fixation TRs at end of run

# ==============================================================================
# DIRECTORY & FILE PATHS
# ==============================================================================
# Directory where real-time data will appear
watch_dir: "/path/to/realtime/data"

# Directory containing model files
model_dir: "/path/to/model/files"

# Directory containing dcm2niix binary
dcm2niix_dir: "/path/to/dcm2niix"

# Reference directory containing warp files and other reference data
ref_dir: "/path/to/reference/files"

# Path to MNI template file
mni_template: "/path/to/mni/template.nii.gz"

# ==============================================================================
# OPTIONAL LOGGING/DEBUGGING
# ==============================================================================
# Archive directory for storing processed data
archive_dir: "/path/to/archive/directory"

# Log file timestamp (will be set at runtime)
log_file_time: null

# Log directory (if null, will use default location)
log_dir: null
"""

    with open(output_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"Configuration template saved to: {output_path}")
    return output_path

def validate_config(config_or_path, args):
    """
    Validates that a configuration contains all required parameters based on CLI arguments.
    
    Args:
        config_or_path: Either a config dictionary or path to the configuration file to validate
        args: Parsed argument namespace from argparse
        
    Returns:
        tuple: (is_valid, missing_params, validation_messages)
    """
    param_class = {
        'basic': [
            'experiment_name', 'start_run', 'feedback_mode', 'mc_mode', 
            'baseline_trs', 'feedback_trs', 'moving_avg_trs', 'post_url', 'predict_type'
        ],
        'paths': ['watch_dir', 'model_dir', 'dcm2niix_dir'],
        'intermittent_only': [
            'encoding_trs', 'cue_trs', 'wait_trs', 'iti_trs', 
            'trials', 'runEnd_fix_trs'
        ],
        'optional': [
            'script_start_time', 'ref_dir', 'mni_template', 'archive_dir', 'log_dir'
        ],
        'flag_dependent': {
            'dashboard': ['dashboard_base_url'],  # Required if --dashboard flag is used
            'logging': ['log_dir'],               # Required if --logging flag is used
            'debug': ['archive_dir']              # Required if --debug flag is used
        }
    }
    
    # Handle both config dictionary and config file path
    if isinstance(config_or_path, dict):
        config = config_or_path
    else:
        try:
            with open(config_or_path, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            return False, [], [f"Error reading config file: {e}"]
    
    missing_params = []
    validation_messages = []
    
    # Check basic required parameters
    for param in param_class['basic'] + param_class['paths']:
        if param not in config:
            missing_params.append(param)
    
    # Check intermittent-specific parameters if needed
    if config.get('feedback_mode', '').lower() == 'intermittent':
        for param in param_class['intermittent_only']:
            if param not in config:
                missing_params.append(param)
    
    # Check flag-dependent parameters based on CLI arguments
    if hasattr(args, 'dashboard') and args.dashboard:
        for param in param_class['flag_dependent']['dashboard']:
            if param not in config:
                missing_params.append(f"{param} (required when --dashboard flag is used)")
    
    if hasattr(args, 'logging') and args.logging:
        for param in param_class['flag_dependent']['logging']:
            if param not in config:
                missing_params.append(f"{param} (required when --logging flag is used)")
    
    if hasattr(args, 'debug') and args.debug:
        for param in param_class['flag_dependent']['debug']:
            if param not in config:
                missing_params.append(f"{param} (required when --debug flag is used)")
    
    # Check if flag-dependent directory paths exist
    flag_dependent_paths = {
        'dashboard': {},  # dashboard_base_url is a URL, not a path
        'logging': {'log_dir': 'directory'},
        'debug': {'archive_dir': 'directory'}
    }

    for flag, path_checks in flag_dependent_paths.items():
        if hasattr(args, flag) and getattr(args, flag):
            for param, path_type in path_checks.items():
                if param in config and config[param] is not None:
                    if not os.path.exists(config[param]):
                        validation_messages.append(
                            f"Path does not exist: {config[param]} (for {param}, expected {path_type})"
                        )
    
    # Validate feedback mode
    if 'feedback_mode' in config:
        if config['feedback_mode'].lower() not in ['continuous', 'intermittent']:
            validation_messages.append("feedback_mode must be 'continuous' or 'intermittent'")
    
    # # Validate mc_mode
    # if 'mc_mode' in config:
    #     if config['mc_mode'].lower() not in ['afni', 'fsl', 'none']:
    #         validation_messages.append("mc_mode must be 'afni', 'fsl', or 'none'")
    
    # Check if critical paths exist (for directories/files that should exist)
    path_checks = {
        'watch_dir': 'directory',
        'model_dir': 'directory', 
        'dcm2niix_dir': 'directory'
        # Note: watch_dir might not exist yet in debug mode
    }
    
    for path_param, path_type in path_checks.items():
        if path_param in config and config[path_param] is not None:
            if not os.path.exists(config[path_param]):
                validation_messages.append(
                    f"Path does not exist: {config[path_param]} (for {path_param}, expected {path_type})"
                )
    
    # # Validate timing parameters are positive integers
    # timing_params = [
    #     'baseline_trs', 'feedback_trs', 'moving_avg_trs', 
    #     'encoding_trs', 'cue_trs', 'wait_trs', 'iti_trs', 'runEnd_fix_trs'
    # ]
    
    # for param in timing_params:
    #     if param in config:
    #         try:
    #             value = int(config[param])
    #             if value <= 0:
    #                 validation_messages.append(f"{param} must be a positive integer, got {value}")
    #         except (ValueError, TypeError):
    #             validation_messages.append(f"{param} must be an integer, got {config[param]}")
    
    # # Validate trials parameter
    # if 'trials' in config:
    #     try:
    #         value = int(config['trials'])
    #         if value <= 0:
    #             validation_messages.append(f"trials must be a positive integer, got {value}")
    #     except (ValueError, TypeError):
    #         validation_messages.append(f"trials must be an integer, got {config['trials']}")
    
    # # Validate start_run parameter
    # if 'start_run' in config:
    #     try:
    #         value = int(config['start_run'])
    #         if value <= 0:
    #             validation_messages.append(f"start_run must be a positive integer, got {value}")
    #     except (ValueError, TypeError):
    #         validation_messages.append(f"start_run must be an integer, got {config['start_run']}")
    
    # # Check URL format for post_url
    # if 'post_url' in config:
    #     if not config['post_url'].startswith(('http://', 'https://')):
    #         validation_messages.append("post_url must be a valid URL starting with http:// or https://")
    
    # # Check URL format for dashboard_base_url if present
    # if 'dashboard_base_url' in config:
    #     if not config['dashboard_base_url'].startswith(('http://', 'https://')):
    #         validation_messages.append("dashboard_base_url must be a valid URL starting with http:// or https://")
    
    is_valid = len(missing_params) == 0 and len(validation_messages) == 0
    
    if missing_params:
        validation_messages.append(f"Missing required parameters: {', '.join(missing_params)}")
    
    if config.get('mni_template') is not None:
        print("Warning: Using MNI Template in alignment")
    
    return is_valid, missing_params, validation_messages

def generate_derived_config(config, args):
    """
    Generates derived configuration parameters and sets up directories/files.
    
    Args:
        config (dict): Configuration dictionary
        args: Parsed argument namespace from argparse
        
    Returns:
        dict: Updated configuration with derived parameters
    """
    # Get metadata from args
    config['subject_id'] = args.subjectid
    config['session_num'] = args.session
    
    # Correct case formatting
    config['feedback_mode'] = config['feedback_mode'].lower()
    config['mc_mode'] = config['mc_mode'].lower()
    
    # Calculate timing parameters based on feedback mode
    config['run_count'] = int(config['start_run']) - 1
    config['REALTIME_TIMEOUT'] = 0.1  # seconds for real-time requests
    
    if config['feedback_mode'] == 'continuous':
        config['run_trs'] = config['baseline_trs'] + config['feedback_trs']
        config['feedback_calc_trs'] = np.arange(config['baseline_trs'], 
                                               config['feedback_trs'] + config['baseline_trs'])
    elif config['feedback_mode'] == 'intermittent': 
        config['trial_trs'] = (config['encoding_trs'] + config['cue_trs'] + 
                              config['wait_trs'] + config['feedback_trs'] + config['iti_trs'])
        config['run_trs'] = ((config['baseline_trs'] + config['trials'] * config['trial_trs']) + 
                            config['runEnd_fix_trs'])
        config['trs_to_score_calc'] = config['cue_trs'] + config['wait_trs']
        config['feedback_calc_trs'] = (config['baseline_trs'] + config['trs_to_score_calc'] + 
                                      np.arange(config['trials']) * config['trial_trs'] - 1)
   
    # Generate standard directories based on current working dir
    config.setdefault('standard_dir', os.getcwd() + '/standard')
    config.setdefault('proc_dir', os.getcwd() + '/proc')
    
    # Generate ref_dir if not defined in config
    if not config.get('ref_dir'):
        config['ref_dir'] = os.getcwd() + '/ref/' + config['subject_id']
    
    # Generate model_dir (clf_dir) if not defined
    if not config.get('model_dir'):
        config['model_dir'] = os.getcwd() + '/mni_clf'
    
    # Generate log_dir if not defined
    if not config.get('log_dir'):
        config['log_dir'] = os.getcwd() + '/log'
        if not os.path.exists(config['log_dir']):
            os.makedirs(config['log_dir'])
    
    # # Set up watch_dir based on debug mode
    # if hasattr(args, 'debug') and args.debug:
    #     # Keep the configured watch_dir for debug mode
    #     pass
    # else:
    #     # Modify watch_dir to include subject and session info for real mode
    #     try:
    #         config['watch_dir'] = glob.glob(config['watch_dir'] + '/*.' + 
    #                                       args.subjectid + '_' + str(args.session) + '/')[0]
    #     except IndexError:
    #         print(f"Warning: Could not find subject-specific directory in {config['watch_dir']}")
    
    # Get specific files (with error handling)
    try:
        config['rfi_file'] = glob.glob(config['ref_dir'] + '/*rfi.nii.gz')[0]
    except IndexError:
        print(f"Warning: Could not find RFI file in {config['ref_dir']}")
        config['rfi_file'] = None
    
    try:
        config['clf_file'] = glob.glob(config['model_dir'] + '/*mni_clf.p')[0]
    except IndexError:
        print(f"Warning: Could not find classifier file in {config['model_dir']}")
        config['clf_file'] = None
    
    try:
        config['warp_file'] = glob.glob(config['ref_dir'] + '/*warp_displacement.nii.gz')[0]
    except IndexError:
        print(f"Warning: Could not find warp file in {config['ref_dir']}")
        config['warp_file'] = None
    
    # Set up target class (optional) - removed for now
    # try:
    #     config['target_class'] = int(np.loadtxt(config['ref_dir'] + '/class.txt'))
    # except:
    #     config['target_class'] = -1
    
    # # Set up logging parameters
    # if hasattr(args, 'logging') and args.logging:
    #     config['logging_bool'] = True
    #     if not config.get('log_file_time'):
    #         config['log_file_time'] = int(np.floor(time.time()))
    # else:
    #     config['logging_bool'] = False
    
    # # Set up dashboard parameters
    # if hasattr(args, 'dashboard') and args.dashboard:
    #     config['dashboard_bool'] = True
    #     if config.get('dashboard_base_url'):
    #         config['dashboard_mc_url'] = config['dashboard_base_url'] + '/mc_data'
    #         config['dashboard_clf_url'] = config['dashboard_base_url'] + '/clf_data'
    #         config['dashboard_shutdown_url'] = config['dashboard_base_url'] + '/shutdown'
    # else:
    #     config['dashboard_bool'] = False
    
    # # Set up archive parameters based on debug flag (replaces archive_data)
    # config['archive_bool'] = hasattr(args, 'debug') and args.debug
    
    return config

def setup_config(config_path, args):
    """
    Reads a YAML configuration file and returns the configuration as a dictionary.
    Args:
        config_path (str): Path to the YAML configuration file.
        args: Parsed argument namespace from argparse
    Returns:
        dict: Configuration parameters.
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading config file {config_path}: {e}")
        sys.exit(1)
    
    # Validate the configuration
    is_valid, missing_params, validation_messages = validate_config(config, args)
    if not is_valid:
        print("Configuration validation failed:")
        for message in validation_messages:
            print(f"  - {message}")
        sys.exit(1)
    
    # Generate derived parameters and set up directories
    config = generate_derived_config(config, args)
    
    return config

def write_log_header(log_file):
    log_file.write('time,event,tr\n')

def write_log(log_file, start_time, event_name, count):
    log_file.write(str(time.time()-start_time)+','+event_name+','+str(count)+'\n')

def initialize_log(script_start_time, log_dir=None):
    if log_dir is None:
        log_dir = os.getcwd() + '/log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file_time = int(np.floor(time.time()))
    log_file_name = os.path.join(log_dir, str(log_file_time) + '_event.log')
    log_file = open(os.path.normpath(log_file_name),'
    write_log_header(log_file)
    write_log(log_file, script_start_time, 'startup', 0)

    
def send_loop_output(out_data, config):
    payload = {"clf_outs": list(out_data[:-1]),
            "target_class": out_data[-1],
            "feedback_num": config['feedback_count']}
    print('payload:', payload) # dw
    try:
        r.post(config['post_url'], json=payload, timeout=config['REALTIME_TIMEOUT'])
        # dw: how to print out the current url?
    except:
        pass

# return: feedback number, array w/ classifier output, not cumulative (new file for each rep)
# def read_loop_output