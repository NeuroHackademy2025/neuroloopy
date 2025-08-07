import numpy as np

# Global config will be set by the main application
config = {'predict_type': 'prob_est'}  # Default value

def apply_classifier(clf, data, num_roi_voxels, logging_bool=False, predict_type=None):
    """
    Apply a trained classifier to ROI data for real-time neurofeedback.

    This function reshapes ROI data into the expected input format and applies a classifier
    to generate predictions or evidence scores, depending on configuration settings.
    In debugging mode, it generates random input data to simulate predictions.

    Parameters
    ----------
    clf : object
        Trained classifier object. Must implement:
        - `predict(X)`: returns class/category prediction(s)
        - `predict_evidence(X)`: returns probability/confidence scores (e.g., softmax output)

    data : buffer-like or array-like
        Flattened 1D buffer or array of ROI voxel values of length `num_roi_voxels`.

    num_roi_voxels : int
        Number of voxels in the ROI; used to reshape the data into shape (1, num_roi_voxels)
        before passing it to the classifier.

    logging_bool : bool, optional (default=False)
        If True, enables debug mode, where predictions are computed on random data.
        This is useful for testing pipeline connectivity without real neuroimaging data.
    
    predict_type : str, optional (default=None)
        Type of prediction to return. If None, uses global config.
        Options: 'category', 'prob_est'

    Returns
    -------
    clf_result : array-like
        Output of the classifier. If `predict_type` is:
        - `'category'`: returns predicted class label(s)
        - `'prob_est'`: returns probability/confidence estimates

    Notes
    -----
    This function relies on either a provided predict_type or a global `config` dictionary containing:
        config['predict_type']: str
            Either `'category'` or `'prob_est'`, determining the type of classifier output.

    Raises
    ------
    KeyError
        If 'predict_type' is not found in the global config and not provided as parameter.
    """
    # Use provided predict_type or fall back to global config
    if predict_type is None:
        predict_type = config.get('predict_type', 'prob_est')
    
    if not logging_bool:
        if predict_type == 'category':
            clf_result = clf.predict(np.ndarray((1, num_roi_voxels), buffer=data))
        elif predict_type == 'prob_est':
            # Handle different classifier types
            if hasattr(clf, 'predict_evidence'):
                clf_result = clf.predict_evidence(np.ndarray((1, num_roi_voxels), buffer=data))
            elif hasattr(clf, 'predict_proba'):
                clf_result = clf.predict_proba(np.ndarray((1, num_roi_voxels), buffer=data))
            else:
                # Fallback to regular predict
                clf_result = clf.predict(np.ndarray((1, num_roi_voxels), buffer=data))
    else:
        if predict_type == 'category':
            clf_result = clf.predict(np.random.normal(0, 1, (1, num_roi_voxels)))
        else:
            # Generate random probabilities for debugging
            clf_result = np.random.random((1, 2))  # Assuming binary classification
            clf_result = clf_result / clf_result.sum()  # Normalize to sum to 1
        print("[DEBUGGING MODE]: classifier values are random")
    
    return clf_result

def set_config(new_config):
    """
    Set the global configuration for the analysis module.
    
    Parameters
    ----------
    new_config : dict
        Configuration dictionary containing predict_type and other parameters
    """
    global config
    config = new_config