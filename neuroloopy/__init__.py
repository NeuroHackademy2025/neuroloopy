"""
neuroloopy: Real-time fMRI neurofeedback processing

A Python package for real-time fMRI data processing and neurofeedback delivery.
"""

__version__ = "0.1.0"
__author__ = "neuroloopy development team"

# Import main components for easy access
from .cli import main
from .watcher import start_watcher, InstaWatcher
from .preproc import ref_img, rt_img
from .anal import apply_classifier
from .utils import setup_config, generate_config_template

__all__ = [
    'main',
    'start_watcher', 
    'InstaWatcher',
    'ref_img',
    'rt_img', 
    'apply_classifier',
    'setup_config',
    'generate_config_template'
]
