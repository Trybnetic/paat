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
from tensorflow.keras import models

# Hide GPU from visible devices
tf.config.set_visible_devices([], 'GPU')
#tf.compat.v1.disable_eager_execution()

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def detect_time_in_bed_weitz2024(data, sample_freq, resampled_frequency="1min", means=None, stds=None, model=None):
    """
    Infer time in bed from raw acceleration signal.

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
    if resampled_frequency:
        data = data[['X', 'Y', 'Z']].resample(resampled_frequency).mean()

    X = data.reset_index()[["Y", "X", "Z"]].values.copy()

    # If no means and stds are given, calculate subject's mean and std
    # to normalize by this
    if not means or not stds:
        means, stds = X.mean(axis=0), X.std(axis=0)

    # Normalize input
    X = (X - means) / stds        

    # Load model if not specified
    if not model:
        model_path = os.path.join(os.path.pardir, os.path.dirname(__file__), 'models', 'TIB_model.h5')
        model = models.load_model(model_path)

    predictions = (model.predict(X[np.newaxis], verbose=0).squeeze() >= .5)

    seconds = pd.Timedelta(resampled_frequency).seconds
    predictions = np.repeat(predictions, seconds * sample_freq)

    return predictions
