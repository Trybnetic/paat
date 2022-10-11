"""
Preprocessing Module
--------------------

*paat.preprocessing* provides functions to process the raw acceleration signals.

"""

import logging
import sys
from multiprocessing import cpu_count

import numpy as np
import resampy
import pandas as pd
from sklearn.linear_model import LinearRegression

try:
    from joblib import Parallel
    from joblib import delayed
except ImportError:
    Parallel = None
    delayed = None

from .visualizations import autocalibration_plots


def resample_acceleration(data, from_hz, to_hz, use_parallel=False, num_jobs=cpu_count(), verbose=False):
    """
    Resample acceleration data to different frequency. For example, convert 100hz data to 30hz data.
    Enables upsampling (from lower to higher frequency), or downsampling (from higher to lower frequency)

    Uses the resampy python module.
    see: https://github.com/bmcfee/resampy

    Used in this paper:
    Smith, Julius O. Digital Audio Resampling Home Page Center for Computer Research in Music and Acoustics (CCRMA), Stanford University, 2015-02-23. Web published at http://ccrma.stanford.edu/~jos/resample/.

    Parameters
    ----------
    data : np.array
        numpy array with acceleration data, can be more than one dimension
    from_hz : int
        original sample frequency of the data (this is usually the frequency the device was set to during initialization)
    to_hz : int
        the sampling frequency to convert to.
    use_parallel : Bool (optional)
        if set to True, then individual axis will be processed in parallel to speed up computational time. Defaults to False
    num_jobs : int (optional)
        if 'use_parallel' is set to True, then 'num_jobs' defines how many parallel jobs are executed at the same time. This typically is the number of
        hyperthreads. Also note that for triaxial data, even if n_jobs > 3 axes, it can only process 3 at the same time.
    verbose : bool (optional)
        if set to True, then output debug messages to console and log file.


    Returns
    -------
    new_data : np.array
        new numpy array with resampled acceleration data

    """

    logging.info('Start %s', sys._getframe().f_code.co_name)

    # calculate number of 1 sec samples (note that hz is the frequency per second)
    num_seconds = len(data) // from_hz

    # calculate number of new samples required when data is resampled
    num_samples = num_seconds * to_hz

    # get number of axes in the data. These are the columns of the array (so if we have xyz then this is 3)
    axes = data.shape[1]

    # create new empty array that we can populate with the resampled data
    new_data = np.zeros((num_samples, axes))

    if use_parallel:

        # use parallel processing to speed up processing time
        executor = Parallel(n_jobs=num_jobs, backend='multiprocessing')

        # create tasks so we can execute them in parallel
        tasks = (delayed(resample)(data[:, ii], from_hz, to_hz, ii) for ii in range(axes))

        # execute tasks in parallel. It returns the resampled columns and column index i
        for ii, column_data in executor(tasks):
            new_data[:, ii] = column_data

    else:
        # loop over each of the columns of the original data, resample, and then add to the new_data array
        for ii in range(axes):
            _, new_data[:, ii] = resample(data[:, ii], from_hz, to_hz, ii, verbose)

    return new_data


def resample(data, from_hz, to_hz, index, verbose):
    """
    Resample data from_hz to to_hz

    Parameters
    ----------
    data: np.array(n_samples, 1)
        numpy array with single column
    from_hz: int
        original sample frequency of the data (this is usually the frequency the device was set to during initialization)
    to_hz: int
        the sampling frequency to convert to.
    index: int
        column index. Is used when use_parallel is set to True and the index is then used to know which column index is being returned.
    verbose : bool (optional)
        if set to True, then output debug messages to console and log file.

    Returns
    -------
    index: int
        column index, see above
    new_data: np.array(n_samples, 1)
        new numpy array with resampled acceleration data

    """

    if verbose:
        logging.debug('Processing axis %s', index)

    return index, resampy.resample(data, from_hz, to_hz)


def rescale(acceleration, acceleration_scale=256.):
    """
    Rescale raw acceleration data to g values

    Parameters
    ----------
    acceleration : np.array()
        array with YXZ acceleration data (in integers otherwise no scaling required)
    acceleration_scale : float (optional)
        value to scale the acceleration

    Returns
    -------
    scaled_log_data : np.array()
        log_data scaled by acceleration scale

    """

    try:

        # calculate the scaling factor
        scale_factor = 1. / float(acceleration_scale)

        # apply scaling and return
        return acceleration * scale_factor

    except Exception as msg:
        logging.error('Error rescaling log data: %s', msg)


def calibrate(acc, hz, std_threshold=0.013, sliding_window=10, save_diagnostic_plot_to=None):
    """
    Autocalibrate the acceleration data based on epochs with low activity based on

    Van Hees, V. T., Fang, Z., Langford, J., Assah, F., Mohammad, A., Da Silva, I. C.,
    ... & Brage, S. (2014). Autocalibration of accelerometer data for free-living
    physical activity assessment using local gravity and temperature: an evaluation on
    four continents. Journal of applied physiology, 117(7), 738-744.
    https://doi.org/10.1152/japplphysiol.00421.2014

    The method calculates the parameters of a linear transformation of the input
    data to achieve a vector magnitude of 1g during low activity episodes as then
    the vector magnitude of the acceleration signal should equal earth's gravitation.

    Parameters
	---------
	acc : np.array(samples, 3) or pd.DataFrame
		acceleration data
    hz : int
        sample frequency of the data
    std_threshold : float
        the threshold of the standard deviation of a segment to be considered low
        activity
    sliding_window : int
        length of the segments in seconds
    save_diagnostic_plot_to : str or os.Path
        file path to where the diagnostic plots should be stored

	Returns
	--------
	acc_tranformed : np.array(samples, 3)
		a numpy array of the same shape as acc with the transformed data
    """

    if isinstance(acc, pd.DataFrame):
        if len(acc.columns) != 3:
            raise ValueError("DataFrame should only contain the accelerometer data.")

        if all([col in acc.columns for col in ["X","Y", "Z"]]):
            acc = acc.values
        else:
            raise ValueError('DataFrame does not contain "X", "Y" and "Z" data.')

    sliding_window_sec = sliding_window * hz

    segments = acc[:len(acc) - len(acc) % sliding_window_sec].reshape((len(acc)//sliding_window_sec, sliding_window_sec, 3))

    is_below_threshold = (segments.std(axis=1) < std_threshold).all(axis=1)

    X = segments[is_below_threshold].mean(axis=1)

    error_start = abs(np.linalg.norm(X, axis=1) - 1).mean()

    has_values_over_300mg = ((X > .300).sum(axis=0) > 0).all()
    has_values_under_minus_300mg = ((X < -.300).sum(axis=0) > 0).all()

    # Only autocalibrate if each axis has values above 300mg and below -300mg
    if not (has_values_over_300mg and has_values_under_minus_300mg):
        logging.warn("No autocalibration performed due to too sparse data.")
        return acc, (1, 1, 1), (0, 0, 0), error_start, None

    if save_diagnostic_plot_to:
        autocalibration_plots(X, file_path=save_diagnostic_plot_to)

    # Under ideal calibration each vector in rest position would have a norm of one
    Y = X / np.linalg.norm(X, axis=1)[np.newaxis].T

    model_X = LinearRegression().fit(X[:, 0, np.newaxis], Y[:, 0, np.newaxis])
    model_Y = LinearRegression().fit(X[:, 1, np.newaxis], Y[:, 1, np.newaxis])
    model_Z = LinearRegression().fit(X[:, 2, np.newaxis], Y[:, 2, np.newaxis])

    acc_tranformed = acc.copy()
    acc_tranformed[:, 0] = model_X.predict(acc[:, 0, np.newaxis]).squeeze()
    acc_tranformed[:, 1] = model_Y.predict(acc[:, 1, np.newaxis]).squeeze()
    acc_tranformed[:, 2] = model_Z.predict(acc[:, 2, np.newaxis]).squeeze()

    X_transformed = X.copy()
    X_transformed[:, 0] = model_X.predict(X[:, 0, np.newaxis]).squeeze()
    X_transformed[:, 1] = model_Y.predict(X[:, 1, np.newaxis]).squeeze()
    X_transformed[:, 2] = model_Z.predict(X[:, 2, np.newaxis]).squeeze()

    error_end = abs(np.linalg.norm(X_transformed, axis=1) - 1).mean()

    scale = tuple(np.concatenate((model_X.coef_[0], model_Y.coef_[0], model_Z.coef_[0])))
    offset = tuple(np.concatenate((model_X.intercept_, model_Y.intercept_, model_Z.intercept_)))

    logging.info(f"Data autocalibrated with scale = {scale}, offset = {offset}")

    return acc_tranformed, scale, offset, error_start, error_end
