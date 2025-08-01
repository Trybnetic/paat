"""
Sleep Module
------------

*paat.sleep* provides functions to detect periods of sleep in the raw
acceleration signals.

"""
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import pandas as pd
import numpy as np
import tensorflow as tf
import keras


def detect_time_in_bed_weitz2024(data, sample_freq, resampled_frequency="1min", means=None, stds=None, model=None):
    """
    Infer time in bed from raw acceleration signal using the method of Weitz et al. (2025).

    References
    ----------

    Weitz, M., Syed, S., Hopstock, L. A., Morseth, B., Henriksen, A., & Horsch, A. (2025). Automatic time in bed detection from hip-worn accelerometers for large epidemiological studies: The Tromsø Study. *PLOS ONE*, 20(5), e0321558. https://doi.org/10.1371/journal.pone.0321558


    Parameters
    ----------
    data : DataFrame
        a DataFrame containg the raw acceleration data
    sample_freq : int
        the sampling frequency in which the data was recorded
    resampled_frequency : str (optional)
        a str indicating to what frequency the data should be resampled. This depends
        on the model used to predict, defaults to 1min.
    means : array_like (optional)
        a numpy array with the channel means, will be calculated for the sample
        if not specified
    stds : array_like (optional)
        a numpy array with the channel stds, will be calculated for the sample
        if not specified
    model : keras.Model (optional)
        a loaded keras custom model.

    Returns
    -------
    predicted_time_in_bed : np.array (n_samples,)
        a numpy array indicating whether the values of the acceleration data were spent in bed

    """
    n_data = len(data)

    if resampled_frequency:
        data = data[['X', 'Y', 'Z']].resample(resampled_frequency).mean()

    # Order data as YXZ as this is how the model was trained
    X = data.reset_index()[["Y", "X", "Z"]].values.copy()

    # If no means and stds are given, calculate subject's mean and std
    # to normalize by this
    if not means or not stds:
        means, stds = X.mean(axis=0), X.std(axis=0)

    # Normalize input
    X = (X - means) / stds        

    # Load model if not specified
    if not model:
        model_path = os.path.join(os.path.pardir, os.path.dirname(__file__), 'models', 'TIB_model.pb')
        model= keras.layers.TFSMLayer(model_path, call_endpoint='serving_default')

    predictions = (model(X[np.newaxis])["output_0"].numpy().squeeze() >= .5)

    seconds = pd.Timedelta(resampled_frequency).seconds
    # Slices the predictions to the length of the provided data
    # This can be relecant if the provided data has incomplete minutes at the start or the end
    predictions = np.repeat(predictions, seconds * sample_freq)[:n_data]

    return predictions
