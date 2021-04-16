"""
paat.preprocessing
------------------

*paat.preprocessing* provides functions to process the raw acceleration signals.

"""

import logging
import sys
from multiprocessing import cpu_count

import numpy as np
import resampy # to resample frequency

try:
    from joblib import Parallel
    from joblib import delayed
except ImportError:
    Parallel = None
    delayed = None


def calculate_vector_magnitude(data, minus_one = False, round_negative_to_zero = False, dtype = np.float32):
    r"""Calculate the vector magnitude of the acceleration data.

    The vector magnitude of the acceleration is calculated as the Euclidian Norm.

    .. math:: \sqrt{y^2 + x^2 + z^2}

    if minus_one is set to True then it it is the Euclidian Norm Minus One.

    .. math:: \sqrt{y^2 + x^2 + z^2} - 1

    if round_negative_to_zero all negative values are clipped.

    Parameters
    ----------
    data: np.array (acceleration values, axes)
       numpy array with acceleration data
    minus_one: Boolean (optional)
       If set to True, the calculate the vector magnitude minus one, also known as the ENMO (Euclidian Norm Minus One)
    round_negative_to_zero: Boolean (optional)
       If set to True, round negative values to zero
    dtype: np.dtype (optional)
       set the data type of the return array. Standard float 16, but can be set to better precision

    Returns
    -------
    vector_magnitude: np.array (acceleration values, 1)(np.float)
       numpy array with vector magnitude of the acceleration
    """

    # change dtype of array to float32 (also to hold scaled data correctly). The original unscaled data is stored as int16, but when we want to calculate the vector we exceed the values that can be stored in 16 bit
    data = data.astype(dtype = np.float32)

    try:

        # calculate the vector magnitude on the whole array
        vector_magnitude = np.sqrt(np.sum(np.square(data), axis=1)).astype(dtype=dtype)

        # check if minus_one is set to True, if so, we need to calculate the ENMO
        if minus_one:
            vector_magnitude -= 1

        # if set to True, round negative values to zero
        if round_negative_to_zero:
            vector_magnitude = vector_magnitude.clip(min=0)

        # reshape the array into number of acceleration values, 1 column
        return vector_magnitude.reshape(data.shape[0], 1)

    except Exception as e:

        logging.error('[{}] : {}'.format(sys._getframe().f_code.co_name,e))
        exit(1)


def resample_acceleration(data, from_hz, to_hz, use_parallel = False, num_jobs = cpu_count(), verbose = False):
    """
    Resample acceleration data to different frequency. For example, convert 100hz data to 30hz data.
    Enables upsampling (from lower to higher frequency), or downsampling (from higher to lower frequency)

    Uses the resampy python module.
    see: https://github.com/bmcfee/resampy

    Used in this paper:
    Smith, Julius O. Digital Audio Resampling Home Page Center for Computer Research in Music and Acoustics (CCRMA), Stanford University, 2015-02-23. Web published at http://ccrma.stanford.edu/~jos/resample/.

    Parameters
    ----------
    data: np.array
        numpy array with acceleration data, can be more than one dimension
    from_hz: int
        original sample frequency of the data (this is usually the frequency the device was set to during initialization)
    to_hz: int
        the sampling frequency to convert to.
    use_parallel: Bool (optional)
        if set to True, then individual axis will be processed in parallel to speed up computational time. Defaults to False
    num_jobs: int (optional)
        if 'use_parallel' is set to True, then 'num_jobs' defines how many parallel jobs are executed at the same time. This typically is the number of
        hyperthreads. Also note that for triaxial data, even if n_jobs > 3 axes, it can only process 3 at the same time.
    verbose: bool (optional)
        if set to True, then output debug messages to console and log file.


    Returns
    --------
    new_data: np.array
        new numpy array with resampled acceleration data
    """

    logging.info('Start {}'.format(sys._getframe().f_code.co_name))

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
        executor = Parallel(n_jobs = num_jobs, backend = 'multiprocessing')

        # create tasks so we can execute them in parallel
        tasks = (delayed(resample)(data[:,i], from_hz, to_hz, i) for i in range(axes))

        # execute tasks in parallel. It returns the resampled columns and column index i
        for i, column_data in executor(tasks):

            # add column data to correct column index
            new_data[:,i] = column_data

        # finished and return new data
        return new_data

    else:
        # loop over each of the columns of the original data, resample, and then add to the new_data array
        for i in range(axes):

            _, new_data[:,i] = resample(data[:,i], from_hz, to_hz, i, verbose)

        return new_data


"""
    Internal Helper Function
"""
def resample(data, from_hz, to_hz, index, verbose):
    """
    Resample data from_hz to to_hz

    data: np.array(n_samples, 1)
        numpy array with single column
    from_hz: int
        original sample frequency of the data (this is usually the frequency the device was set to during initialization)
    to_hz: int
        the sampling frequency to convert to.
    index: int
        column index. Is used when use_parallel is set to True and the index is then used to know which column index is being returned.

    Returns
    -------
    index: int
        column index, see above
    new_data: np.array(n_samples, 1)
        new numpy array with resampled acceleration data
    """

    if verbose:
        logging.debug('Processing axis {}'.format(index))

    return index, resampy.resample(data, from_hz, to_hz)
