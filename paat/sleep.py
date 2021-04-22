"""
Sleep Module
------------

*paat.sleep* provides functions to detect periods of sleep in the raw
acceleration signals.

"""

import numpy as np


# pylint: disable=C0103
def cole_kripke(data, weights=[106, 54, 58, 76, 230, 74, 67], P=0.001):
    """
    Implementation of the Algorithm proposed by Cole et al. (1992).

    See
    Cole, R. J., Kripke, D. F., Gruen, W., Mullaney, D. J., & Gillin, J. C. (1992). Automatic
    sleep/wake identification from wrist activity. Sleep, 15(5), 461-469.

    Parameters
    ----------
    data: np.array
        a numpy array containing the the recorded data of one patient over time.
    weights: tuple, list or np.array
        a 7-tuple of weights for the entries of the corresponding window. The
        default values correspond to the optimal parameters proposed for one
        minute epochs in Cole et al. (1992)
    P: float
        a scale factor for the entire equation

    Returns
    -------
    sleep_data : np.array
        a boolean numpy array stating whether the epoch is considered to be asleep

    """

    # Actigraph treats missing epochs as 0, see https://actigraphcorp.force.com/support/
    # s/article/Where-can-I-find-documentation-for-the-Sadeh-and-Cole-Kripke-algorithms
    data = np.concatenate([[0] * 4, data, [0] * 2])

    sliding_windows = np.stack([data[xx:xx-6] for xx in range(6)], axis=-1)

    def _score(window, weights=weights, P=P):
        return P * sum([xx * yy for xx, yy in zip(window, weights)])

    sleep_data = np.apply_along_axis(_score, 1, sliding_windows)

    return sleep_data < 1


def sadeh(data, weights=[7.601, 0.065, 1.08, 0.056, 0.703]):
    """
    Implementation of the Algorithm proposed by Sadeh et al. (1994).

    See
    Sadeh, A., Sharkey, M., & Carskadon, M. A. (1994). Activity-based sleep-wake
    identification: an empirical test of methodological issues. Sleep, 17(3), 201-207.

    Parameters
    ----------
    data: np.array
        a numpy array containing the the recorded data of one patient over time.
    weights: tuple, list or np.array
        a 5-tuple of weights for the different parameters. The default values
        correspond to the optimal parameters proposed in Sadeh et al. (1994)
    P: float
        a scale factor for the entire equation

    Returns
    -------
    sleep_data : np.array
        a boolean numpy array stating whether the epoch is considered to be asleep

    """

    # Actigraph treats missing epochs as 0, see https://actigraphcorp.force.com/support/
    # s/article/Where-can-I-find-documentation-for-the-Sadeh-and-Cole-Kripke-algorithms
    data = np.concatenate([[0] * 5, data, [0] * 6])

    sliding_windows = np.stack([data[xx:xx-11] for xx in range(11)], axis=-1)

    def _score(window, weights=weights):

        if window[5] == 0:
            log_res = 0  # use 0 if epoch count is zero
        else:
            log_res = np.log(window[5])

        return weights[0] - (weights[1] * np.average(window)) - (weights[2] * np.sum((window >= 50) & (window < 100))) - (weights[3] * np.std(window)) - (weights[4] * log_res)

    sleep_data = np.apply_along_axis(_score, 1, sliding_windows)

    return sleep_data > -4


def detect_sleep_time(data, method="sadeh"):
    """
    Convinience function to detect sleep times using default parameters. For
    more sophisticated analysis refer to the seperate implementations of the
    sleep scoring algorithms


    Parameters
    ----------
    data: np.array
        a numpy array containing the the recorded data of one patient over time.

    Returns
    -------
    sleep_data : np.array
        a boolean numpy array stating whether the epoch is considered to be asleep

    """

    if method == "sadeh":
        return sadeh(data)
    elif method == "cole_kripke":
        return cole_kripke(data)
    else:
        raise NotImplementedError("Method '{}' is not implemented, yet.".format(method))
