"""
Features Module
---------------

*paat.features* provides functions to compute various features from the raw
acceleration signal.

"""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def calculate_vector_magnitude(data, minus_one=False, round_negative_to_zero=False, dtype=np.float32):
    r"""
    Calculate the vector magnitude of the acceleration data.

    Parameters
    ----------
    data : array_like
        numpy array with acceleration data
    minus_one : Boolean (optional)
        If set to True, the calculate the vector magnitude minus one, also known as the ENMO (Euclidian Norm Minus One)
    round_negative_to_zero : Boolean (optional)
        If set to True, round negative values to zero
    dtype : np.dtype (optional)
        set the data type of the return array. Standard float 16, but can be set to better precision


    Returns
    -------
    vector_magnitude : np.array (acceleration values, 1)(np.float)
       numpy array with vector magnitude of the acceleration


    Notes
    -----
    The vector magnitude of the acceleration is calculated as the Euclidian Norm.

    .. math:: \sqrt{y^2 + x^2 + z^2}

    if minus_one is set to True then it it is the Euclidian Norm Minus One.

    .. math:: \sqrt{y^2 + x^2 + z^2} - 1

    if round_negative_to_zero all negative values are clipped.

    """

    # change dtype of array to float32 (also to hold scaled data correctly). The original unscaled data is stored as int16, but when we want to calculate the vector we exceed the values that can be stored in 16 bit
    data = data.astype(dtype=np.float32)

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


def calculate_frequency_features(time, acceleration, win_len=60, win_step=60, sample_rate=100, nfft=512, nfilt=40):
    """
    Calculate frequency features from raw acceleration signal.

    Parameters
    ----------
    time : np.array (n_samples x 1)
        a numpy array with time stamps for the observations in values
    acceleration : np.array (n_samples x 3)
        a numpy array with the tri-axial acceleration values in
        the default order of ActiGraph which is ['Y','X','Z'].
    win_len : int (optional)
        an int indicating the window length in seconds
    win_step : int (optional)
        an int indicating the step size between windows in seconds
    sample_rate : float (optional)
        a float indicating the sampling rate in Hz
    nfft: int (optional)
        an int indicating the number of points for the Fourier transform
    nfilt: int (optional)
        an int indicating the number of triangular filters to use

    Returns
    ---------
    time : np.array (n_samples x 1)
        a numpy array with time stamps for the observations in values
    features : np.array (n_samples x 160)
        a numpy array with the 160-dimensional feature vector per time step

    """

    # Calculate Euclidian Norm Minus One for the three axis
    emno = calculate_vector_magnitude(acceleration, minus_one=True).squeeze()

    # Calculate filter banks per signal
    _, fbanks_x = _calculate_filter_banks(acceleration[:, 1], sample_rate, win_len, win_step, nfft=nfft, nfilt=nfilt)
    _, fbanks_y = _calculate_filter_banks(acceleration[:, 0], sample_rate, win_len, win_step, nfft=nfft, nfilt=nfilt)
    _, fbanks_z = _calculate_filter_banks(acceleration[:, 2], sample_rate, win_len, win_step, nfft=nfft, nfilt=nfilt)
    _, fbanks_emno = _calculate_filter_banks(emno, sample_rate, win_len, win_step, nfft=nfft, nfilt=nfilt)

    # Create feature vector
    features = np.hstack([fbanks_x, fbanks_y, fbanks_z, fbanks_emno])

    return time, features


def _hz_to_mel(hz):
    return (2595 * np.log10(1 + (hz / 2) / 700))


def _mel_to_hz(mel):
    return (700 * (10**(mel / 2595) - 1))


def _calculate_filter_banks(signal, sample_rate, win_len, win_step, nfft=512, nfilt=40):
    """
    Calculate filter banks for a signal.

    See https://haythamfayek.com/2016/04/21/speech-processing-for-machine-learning.html
    """
    # Calculate frames on second level to have more data points
    frame_len, frame_step = int(win_len * sample_rate), int(win_step * sample_rate)

    frames = sliding_window_view(signal, frame_len)[::frame_step].copy()
    frames *= np.hamming(frame_len)

    mag_frames = np.absolute(np.fft.rfft(frames, nfft))
    pow_frames = (1.0 / nfft) * (mag_frames ** 2)

    low_freq_mel = 0
    high_freq_mel = _hz_to_mel(sample_rate)

    mel_points = np.linspace(low_freq_mel, high_freq_mel, nfilt + 2)
    hz_points = _mel_to_hz(mel_points)

    bin = np.floor((nfft + 1) * hz_points / sample_rate)

    fbank = np.zeros((nfilt, int(np.floor(nfft / 2 + 1))))
    for mm in range(1, nfilt + 1):
        f_m_minus = int(bin[mm - 1])   # left
        f_m = int(bin[mm])             # center
        f_m_plus = int(bin[mm + 1])    # right

        for kk in range(f_m_minus, f_m):
            fbank[mm - 1, kk] = (kk - bin[mm - 1]) / (bin[mm] - bin[mm - 1])
        for kk in range(f_m, f_m_plus):
            fbank[mm - 1, kk] = (bin[mm + 1] - kk) / (bin[mm + 1] - bin[mm])

    filter_banks = np.dot(pow_frames, fbank.T)
    # remove zeros for log
    filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
    filter_banks = 20 * np.log10(filter_banks)  # dB

    return hz_points, filter_banks
