"""
Sleep Module
------------

*paat.sleep* provides functions to detect periods of sleep in the raw
acceleration signals.

"""

import numpy as np
import torch


def detect_time_in_bed_weitz2022(time, acceleration, resampled_frequency="1min", means=None, stds=None, model_path=None):
    """
    Infer time in bed from raw acceleration signal.

    Parameters
    ----------
    time : np.array (n_samples x 1)
        a numpy array with time stamps for the observations in values
    acceleration : np.array (n_samples x 3)
        a numpy array with the tri-axial acceleration values in
        the default order of ActiGraph which is ['Y','X','Z'].
    resampled_frequency : str (optional)
        a str indicating to what frequency the data should be resampled. This depends
        on the model used to predict, defaults to 1min.
    means : array_like (optional)
        a numpy array with the channel means, will be calculated for the sample
        if not specified
    stds : array_like (optional)
        a numpy array with the channel stds, will be calculated for the sample
        if not specified
    model_path : str (optional)
        an optional path to a custom model.

    Returns
    ---------
    predicted_time_in_bed : np.array (n_samples,)
        a numpy array indicating whether the values of the acceleration data were spent in bed

    """
    if resampled_frequency:
        data = pd.DataFrame(acceleration, columns=['Y', 'X', 'Z'])
        data = data.set_index(time)
        data = data.resample(resampled_frequency).mean()
        X = torch.from_numpy(data[['Y', 'X', 'Z']].values)
    else:
        X = torch.from_numpy(acceleration)

    # The models were trained with XYZ axis ordering while the standard ordering is YXZ
    # Therefore, we have to switch X and Y axis
    X = X[[1,0,2]]
    X = X.float()

    # If no means and stds are given, calculate subject's mean and std
    # to normalize by this
    if not means or not stds:
        means, stds = X.mean(axis=1), X.std(axis=1)

    # Normalize input
    X = (X - means) / stds
    lengths = X.shape[1]

    # Load model if not specified
    if not model_path:
        model_path = os.path.join(os.path.pardir, os.path.dirname(__file__), 'models', 'sleep_weitz.pt')

    model = torch.load(model_path)
    model.eval()

    predicted_time_in_bed = model(X, lengths)
