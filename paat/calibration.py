
"""
Sensor Calibration Module
-------------------------

*paat.calibation* provides functions to calibrate the raw acceleration signal.

"""
import pandas as pd


def estimate_calibration_coefficents(data):
    raise NotImplementedError("Autocalibration is not implemented yet. Please use GGIR to estimate the calibration coefficients.")


def calibrate(acc, scale, offset):
    columns = ["Y", "X", "Z"]
    index = acc.index.copy()
    acc = (scale * acc[columns].values) + offset
    
    acc = pd.DataFrame(acc.astype(float), 
                       columns=columns, 
                       index=index)
    
    return acc[["X", "Y", "Z"]]