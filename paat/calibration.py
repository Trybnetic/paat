
"""
Sensor Calibration Module
-------------------------

*paat.calibation* provides functions to calibrate the raw acceleration signal.

"""
import pandas as pd


def estimate_calibration_coefficents(acc):
    """
    .. warning::
        This function is not implemented yet
    
    Estimates the calibration correction coefficients based on the method proposed 
    by Van Hees et al. (2014)

    References
    ----------
    
    Van Hees, V. T., Fang, Z., Langford, J., Assah, F., Mohammad, A., da Silva, I. C. M., 
    Trenell, M. I., White, T., Wareham, N. J., & Brage, S. (2014). Autocalibration of 
    accelerometer data for free-living physical activity assessment using local gravity 
    and temperature: An evaluation on four continents. *Journal of Applied Physiology*, 
    117(7), 738–744. https://doi.org/10.1152/japplphysiol.00421.2014
    
    Parameters
    ----------
    acc : array_like
        numpy array with acceleration data

    Returns
    -------
    scale : array_like
        numpy array with the scale factors
    offset : array_like
        numpy array with the offset factors
    
    """
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