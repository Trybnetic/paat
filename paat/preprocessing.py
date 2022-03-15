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

try:
    from joblib import Parallel
    from joblib import delayed
except ImportError:
    Parallel = None
    delayed = None


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
