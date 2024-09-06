
"""
Sensor Calibration Module
-------------------------

*paat.calibation* provides functions to calibrate the raw acceleration signal.

"""
import pandas as pd


def estimate_calibration_coefficents(data):
    raise NotImplementedError("Autocalibration is not implemented yet. Please use GGIR to estimate the calibration coefficients.")


def calibrate(acc, scale, offset):
    """
    Calibrates the acceleration data based on the `scale` and `offset` variables.
    
    Parameters
    ----------
    acc : array_like
        numpy array with acceleration data
    scale : array_like
        numpy array with the scale factors
    offset : array_like
        numpy array with the offset factors
    
    Returns
    -------
    acc : array_like
        numpy array with calibrated acceleration data

    """
    columns = ["Y", "X", "Z"]
    index = acc.index.copy()
    acc = (scale * acc[columns].values) + offset
    
    acc = pd.DataFrame(acc.astype(float), 
                       columns=columns, 
                       index=index)
    
    return acc[["X", "Y", "Z"]]