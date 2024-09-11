"""
Features Module
---------------

*paat.features* provides functions to compute various features from the raw
acceleration signal.

"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from scipy import signal
import resampy
from agcounts.extract import get_counts


BROND_COEFF_A = np.array([1, -4.1637, 7.5712, -7.9805, 5.385, -2.4636, 0.89238, 0.06361,
                          -1.3481, 2.4734, -2.9257, 2.9298, -2.7816, 2.4777, -1.6847,
                          0.46483, 0.46565, -0.67312, 0.4162, -0.13832, 0.019852])
BROND_COEFF_B = np.array([0.049109, -0.12284, 0.14356, -0.11269, 0.053804, -0.02023,
                          0.0063778, 0.018513, -0.038154, 0.048727, -0.052577, 0.047847,
                          -0.046015, 0.036283, -0.012977, -0.0046262, 0.012835, -0.0093762,
                          0.0034485, -0.00080972, -0.00019623])

["Y", "X", "Z"]

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
        set the data type of the return array. Standard float 32, but can be set to better precision


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


def calculate_enmo(data, dtype=np.float32):
    """
    Calculate the Euclidean norm minus one from raw acceleration data.
    This function is a wrapper of `calculate_vector_magnitude`.
    
    Parameters
    ----------
    data : array_like
        numpy array with acceleration data
    dtype : np.dtype (optional)
        set the data type of the return array. Standard float 32, but can be set to better precision
    
    Returns
    -------
    vector_magnitude : np.array (acceleration values, 1)(np.float)
       numpy array with the Eucledian Norm Minus One (ENMO) of the acceleration

    """
    if isinstance(data, pd.DataFrame):
        data = data[["Y", "X", "Z"]].values

    return calculate_vector_magnitude(data, minus_one=True, round_negative_to_zero=True)


def calculate_frequency_features(data, win_len=60, win_step=60, sample_rate=100, nfft=512, nfilt=40):
    """
    Calculate frequency features from raw acceleration signal.

    Parameters
    ----------
    data : DataFrame
        a DataFrame containg the raw acceleration data
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
    -------
    time : np.array (n_samples x 1)
        a numpy array with time stamps for the observations in values
    features : np.array (n_samples x 160)
        a numpy array with the 160-dimensional feature vector per time step

    """

    acceleration = data[["Y", "X", "Z"]].values

    # Calculate Euclidian Norm Minus One for the three axis
    emno = calculate_vector_magnitude(acceleration, minus_one=True).squeeze()

    # Calculate filter banks per signal
    _, fbanks_x = _calculate_filter_banks(acceleration[:, 1], sample_rate, win_len, win_step, nfft=nfft, nfilt=nfilt)
    _, fbanks_y = _calculate_filter_banks(acceleration[:, 0], sample_rate, win_len, win_step, nfft=nfft, nfilt=nfilt)
    _, fbanks_z = _calculate_filter_banks(acceleration[:, 2], sample_rate, win_len, win_step, nfft=nfft, nfilt=nfilt)
    _, fbanks_emno = _calculate_filter_banks(emno, sample_rate, win_len, win_step, nfft=nfft, nfilt=nfilt)

    # Create feature vector
    features = np.hstack([fbanks_x, fbanks_y, fbanks_z, fbanks_emno])

    return features


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


def _calc_one_axis_brond_counts(acc, sample_freq, epoch_length, deadband=0.068, peak=2.13, adcResolution=0.0164, A=BROND_COEFF_A, B=BROND_COEFF_B):
    """
    Helper function to process one axis with the Brond algorithm.

    Parameters
    ----------
    acc : array_like
        a numpy containg one axis of the raw acceleration data
    sample_freq : int
        an int indicating at which sampling frequency the data was recorded
    epoch_length: int
        an int indicating the length of the epochs to calculate in seconds
    deadband: float (optional)
        a float indicating the threshold that counts are being calculated. The
        dead band threshold for newer ActiGraph models (GT3X+ and newer models)
        is specified at 0.05g
    peak: float
        a float indicating the upper limit of recording. ActiLife truncates values
        above 2.13g to ensure compatibility with the 8-bit analog to digital
        conversion
    adcResolution: float
        a float indicating the conversion factor for 8bit
    A, B: array_like
        arrays with the filter's nominator and denominator

    Returns
    -------
    counts: array_like
        a numpy array containg the Brønd counts
    """

    # Step 0: Downsample to 30hz if not already
    target_hz = 30
    if sample_freq != target_hz:
        resampled_data = resampy.resample(acc, sample_freq, target_hz)

    # Step 1: Aliasing filter (0.01-7hz)
    B2, A2 = signal.butter(4, np.array([0.01, 7])/(target_hz/2), btype='bandpass')
    dataf = signal.filtfilt(B2, A2, resampled_data)

    # Step 2: ActiGraph filter
    filtered = signal.lfilter(0.965 * B, A, dataf)

    # Step 3, 4 & 5: Downsample to 10hz, clip at peak (2.13g) and rectify
    rectified = np.abs(np.clip(filtered[::3], a_min=-1*peak, a_max=peak))

    # Step 6 & 7: Dead-band and convert to 8bit resolution
    downsampled = np.where(rectified < deadband, 0, rectified) // adcResolution

    # If last epoch was not fully recorded, pad with zeros
    values_per_epoch = 10 * epoch_length
    missing_values = int(np.ceil(len(downsampled) / values_per_epoch) * values_per_epoch) - len(downsampled)
    downsampled = np.pad(downsampled, (0, missing_values), 'constant', constant_values=0)

    # Step 8: Accumulate
    downsampled = downsampled.reshape([-1, 10 * epoch_length])
    counts = np.where(downsampled >= 0, downsampled, 0).sum(axis=1)

    return counts.astype(int)


def calculate_brond_counts(data, sample_freq, epoch_length):
    """
    Create Brønd counts from uniaxial acceleration data. The algorithm was described in

    Brønd, J. C., Andersen, L. B., & Arvidsson, D. (2017). Generating ActiGraph Counts
    from Raw Acceleration Recorded by an Alternative Monitor, Medicine & Science in
    Sports & Exercise, doi: 10.1249/MSS.0000000000001344

    Parameters
    ----------
    data : DataFrame
        a DataFrame containg the raw acceleration data
    sample_freq : int
        an int indicating at which sampling frequency the data was recorded
    epoch_length: int
        an int indicating the length of the epochs to calculate in seconds

    Returns
    -------
    counts: DataFrame
        a DataFrame containg the Brønd counts
    """

    timestamps = data.resample(epoch_length).mean().index

    if isinstance(epoch_length, str):
        epoch_length = pd.Timedelta(epoch_length).seconds


    counts = pd.DataFrame({"Y": _calc_one_axis_brond_counts(data["Y"].values, sample_freq, epoch_length),
                           "X": _calc_one_axis_brond_counts(data["X"].values, sample_freq, epoch_length),
                           "Z": _calc_one_axis_brond_counts(data["Z"].values, sample_freq, epoch_length)},
                           index=timestamps)

    return counts


def calculate_actigraph_counts(data, sample_freq, epoch_length):
    """
    Wrapper function to create ActiGraph counts. A companion paper has been
    submitted by ActiGraph and will be referenced here as soon as it is published.

    Parameters
    ----------
    data: array_like
        a numpy array containing the uniaxial acceleration data
    sample_freq: int
        an int indicating at which sampling frequency the data was recorded
    epoch_length: str
        a string indicating the length of the epochs to calculate

    Returns
    -------
    counts: array_like
        a numpy array containg the ActiGraph counts
    """
    sec_per_epoch = pd.Timedelta(epoch_length).seconds

    counts = get_counts(data[["Y", "X", "Z"]].values, sample_freq, sec_per_epoch)
    index = data.resample(epoch_length).mean().index
    counts = pd.DataFrame(counts, columns=["Y", "X", "Z"], index=index[:len(counts)])
    return counts
