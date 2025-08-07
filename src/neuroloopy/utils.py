"""
Utility functions for fMRI neurofeedback.
"""

import os
import yaml
import time
from pathlib import Path


def load_config(config_path):
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        dict: Configuration dictionary
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def validate_config(config):
    """
    Validate configuration parameters.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_keys = [
        'subject-id', 'session-number', 'start-run',
        'baseline-trs', 'watch-dir', 'post-url'
    ]
    
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        print(f"Missing required configuration keys: {missing_keys}")
        return False
    
    return True


def write_log_header(log_file):
    """
    Write log file header.
    
    Args:
        log_file: Log file object
    """
    log_file.write("Time,Event,Count\n")


def write_log(log_file, start_time, event_name, count):
    """
    Write log entry.
    
    Args:
        log_file: Log file object
        start_time: Start time
        event_name: Event name
        count: Count value
    """
    current_time = time.time()
    elapsed_time = current_time - start_time
    log_file.write(f"{elapsed_time:.3f},{event_name},{count}\n")
    log_file.flush()


def setup_logging(config):
    """
    Setup logging if enabled.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        tuple: (log_file, log_file_time) or (None, None)
    """
    if config.get('logging_bool', False):
        log_file_time = config.get('log_file_time', time.time())
        log_dir = os.getcwd() + '/log'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file_name = f"{log_dir}/{log_file_time}_event.log"
        log_file = open(os.path.normpath(log_file_name), 'w')
        write_log_header(log_file)
        write_log(log_file, log_file_time, 'startup', 0)
        
        return log_file, log_file_time
    else:
        return None, None


def create_directories(config):
    """
    Create necessary directories.
    
    Args:
        config: Configuration dictionary
    """
    directories = [
        config.get('proc-dir', 'proc'),
        config.get('archive-dir', 'archive'),
        config.get('log-dir', 'log')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_subject_paths(config):
    """
    Get subject-specific file paths.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        dict: Path dictionary
    """
    subject_id = config['subject-id']
    base_dir = os.getcwd()
    
    return {
        'ref_dir': f"{base_dir}/ref/{subject_id}",
        'clf_dir': f"{base_dir}/mni_clf",
        'standard_dir': f"{base_dir}/standard"
    }
