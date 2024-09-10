"""
Estimates Module
----------------

*paat.estimates* provides functions to compute physical activity estimates from
the raw acceleration signal.

"""
import pandas as pd
import numpy as np

from . import features


def calculate_pa_levels(data, sample_freq, mvpa_cutpoint, sb_cutpoint, interval="1s"):
    """
    Calculate moderate to vigourous physical activity (MVPA) and sedentary behavior
    based on cutpoints (mvpa_cutpoint and sb_cutpoint) on 1s resolution. The algorithm
    works by

        1. The Euclidian norm minus one (ENMO) is calculated from the triaxial signal
        2. The ENMO is averaged over 1s epochs
        3. These epochs are compared against the mvpa_cutpoint and the sb_cutpoint

    Parameters
    ----------
    data : DataFrame
        a DataFrame containg the raw acceleration data
    sample_freq : int
        the sampling frequency in which the data was recorded
    mvpa_cutpoint : float
        a float indicating the cutpoint between light physical activity and
        moderate-to-vigourous activity
    sb_cutpoint : float
        a float indicating the cutpoint between light physical activity and
        sedentary behavior
    interval : str (optional)
        a str indicating at what frequency the cutpoints are calculated

    Returns
    -------
    pa_levels : np.array (n_samples, 2)
        a numpy array indicating whether the values of the acceleration data are
        moderate-to-vigourous physical activity (first column) or sedentary
        behavior (second column)

    """
    data.loc[:, "EMNO"] = features.calculate_vector_magnitude(data[["Y", "X", "Z"]].values,
                                                              minus_one=True,
                                                              round_negative_to_zero=True)

    if interval:
        tmp = data.resample(interval).mean()
    else:
        tmp = data

    tmp.loc[:, "MVPA"] = (tmp["EMNO"].values >= mvpa_cutpoint)
    tmp.loc[:, "SB"] = (tmp["EMNO"].values <= sb_cutpoint)

    seconds = pd.Timedelta(interval).seconds
    mvpa_vec = np.repeat(tmp["MVPA"].values, seconds * sample_freq)
    sb_vec = np.repeat(tmp["SB"].values, seconds * sample_freq)

    return np.stack((mvpa_vec, sb_vec), axis=1)


def create_activity_column(data, columns=["SB", "MVPA", "Sleep", "Non Wear Time"]):
    """
    Merge the different activity columns into one label column.

    Parameters
    ----------
    data : DataFrame
        a DataFrame containg the raw acceleration data
    columns : array_like
        a list of activity columns in ascending order of importance. The order
        of the list implies which activity overrides which. E.g. the first entry
        would override the second in cases of doubt, etc.

    Returns
    -------
    activity_vec : array_like
        the merged activity vector with the names of columns as entries
    """
    max_chars = max(len(column) for column in columns) + 1
    activity_vec = np.full(data.shape[0], "LPA", dtype=f"<U{max_chars}")

    for column in columns:
        activity_vec[data[column]] = column

    return activity_vec
