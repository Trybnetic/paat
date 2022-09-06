import logging

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from .visualizations import autocalibration_plots


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
	acc : np.array(samples, 3)
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

    sliding_window_sec = sliding_window * hz

    segments = acc[:len(acc) - len(acc) % sliding_window_sec].reshape((len(acc)//sliding_window_sec, sliding_window_sec, 3))

    is_below_threshold = (segments.std(axis=1) < std_threshold).all(axis=1)

    X = segments[is_below_threshold].mean(axis=1)


    has_values_over_300mg = ((X > .300).sum(axis=0) > 0).all()
    has_values_under_minus_300mg = ((X < -.300).sum(axis=0) > 0).all()

    # Only autocalibrate if each axis has values above 300mg and below -300mg
    if not (has_values_over_300mg and has_values_under_minus_300mg):
        logging.warn("No autocalibration performed due to too sparse data.")
        return acc

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

    d_x, d_y, d_z = model_X.intercept_.squeeze(), model_Y.intercept_.squeeze(), model_Z.intercept_.squeeze()
    a_x, a_y, a_z = model_X.coef_.squeeze(), model_Y.coef_.squeeze(), model_Z.coef_.squeeze()

    logging.info(f"Data autocalibrated with d_x = {d_x:.5f}, d_y = {d_y:.5f}, d_z = {d_z:.5f}, " \
                 f"a_x = {a_x:.5f}, a_y = {a_y:.5f}, a_z = {a_z:.5f}.")

    return acc_tranformed
