"""
Neuroloopy - Real-time fMRI neurofeedback package.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .watcher import InstaWatcher, start_watcher
from .preproc import process_volume, convert_dicom_to_nii, map_voxels_to_roi
from .anal import apply_classifier, calculate_feedback, calculate_voxel_sigmas
from .utils import load_config, validate_config, setup_logging, create_directories

__all__ = [
    'InstaWatcher',
    'start_watcher',
    'process_volume',
    'convert_dicom_to_nii',
    'map_voxels_to_roi',
    'apply_classifier',
    'calculate_feedback',
    'calculate_voxel_sigmas',
    'load_config',
    'validate_config',
    'setup_logging',
    'create_directories'
]
