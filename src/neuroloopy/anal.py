"""
Analysis functions for fMRI neurofeedback.
"""

import numpy as np
from scipy.signal import detrend


def apply_classifier(data, classifier, num_roi_voxels, logging_bool=False):
    """
    Apply classifier to volume data.
    
    Args:
        data: Input data
        classifier: Trained classifier object
        num_roi_voxels: Number of ROI voxels
        logging_bool: Enable debug mode
    
    Returns:
        numpy.ndarray: Classifier estimates
    """
    if not logging_bool:
        classifier.predict(np.ndarray((1, num_roi_voxels), buffer=data))
    else:
        classifier.predict(np.random.normal(0, 1, (1, num_roi_voxels)))
        print('debugging mode: classifier value is random')
    
    return classifier.ca.estimates


def calculate_feedback(roi_array, rep, baseline_trs, moving_avg_trs, 
                      voxel_sigmas, classifier, num_roi_voxels, logging_bool=False):
    """
    Calculate feedback from ROI data.
    
    Args:
        roi_array: ROI data array
        rep: Current repetition
        baseline_trs: Baseline TRs
        moving_avg_trs: Moving average TRs
        voxel_sigmas: Voxel standard deviations
        classifier: Trained classifier
        num_roi_voxels: Number of ROI voxels
        logging_bool: Enable debug mode
    
    Returns:
        tuple: (classifier_output, zscore_avg_roi)
    """
    if rep >= (baseline_trs - 1):
        # Detrend the data
        detrend_roi_array = detrend(roi_array[:, :rep + 1], 1)
        
        # Calculate z-scored average
        zscore_avg_roi = np.mean(
            detrend_roi_array[:, -moving_avg_trs:], 1
        ) / voxel_sigmas
        
        # Apply classifier
        clf_out = apply_classifier(
            zscore_avg_roi, classifier, num_roi_voxels, logging_bool
        )
        
        return clf_out, zscore_avg_roi
    
    return None, None


def calculate_voxel_sigmas(roi_array, rep, baseline_trs):
    """
    Calculate voxel standard deviations from baseline.
    
    Args:
        roi_array: ROI data array
        rep: Current repetition
        baseline_trs: Baseline TRs
    
    Returns:
        numpy.ndarray: Voxel standard deviations
    """
    if rep == (baseline_trs - 1):
        voxel_sigmas = np.sqrt(np.var(roi_array[:, :rep + 1], 1))
        voxel_sigmas[np.where(voxel_sigmas == 0)] = 1e6
        return voxel_sigmas
    
    return None
