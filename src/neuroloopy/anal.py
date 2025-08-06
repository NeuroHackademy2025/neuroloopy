import numpy as np

def apply_classifier(clf, data, num_roi_voxels, logging_bool=False):
    """
    Apply a trained machine learning classifier to ROI data for real-time classification.

    Parameters
    ----------
    clf : object
        Trained classifier object with a `predict` method and `predict_evidence` attribute.
    data : array-like, shape (num_roi_voxels,)
        1D array of ROI voxel values to classify.
    num_roi_voxels : int
        Number of voxels in the ROI; used to shape the input data correctly.
    logging_bool : bool, optional (default=False)
        If True, runs in debug mode and outputs random classifier predictions.

    Returns
    -------
    clf_estimates : array-like
        Classifier confidence or probability estimates from the `predict` and `predict_evidence` attributes.
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