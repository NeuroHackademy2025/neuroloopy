import numpy as np

def apply_classifier(clf, data, num_roi_voxels, logging_bool=False):
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

    Returns
    -------
    clf_result : array-like
        Output of the classifier. If `config['predict_type']` is:
        - `'category'`: returns predicted class label(s)
        - `'prob_est'`: returns probability/confidence estimates

    Notes
    -----
    This function relies on a global `config` dictionary containing:
        config['predict_type']: str
            Either `'category'` or `'prob_est'`, determining the type of classifier output.

    Raises
    ------
    KeyError
        If 'predict_type' is not found in the global config.
    """
    if not logging_bool:
        if config['predict_type'] == 'category':
            clf_result = clf.predict(np.ndarray((1, num_roi_voxels), buffer=data))
        elif config['predict_type'] == 'prob_est':
            clf_result = clf.predict_evidence(np.ndarray((1, num_roi_voxels), buffer=data))
    else:
        clf_result = clf.predict(np.random.normal(0, 1, (1, num_roi_voxels)))
        print("[DEBUGGING MODE]: classifier values are random")
    return clf_result