from .estimates import calculate_pa_levels, create_activity_column
from .sleep import detect_sleep_weitz2022, detect_sleep_triaxial_weitz2022
from .wear_time import detect_non_wear_time_syed2021


def annotate(data, sample_freq):
    """
    Function to annotate the raw acceleration data. Performs the standard
    pipeline of paat's functions.

    Parameters
    ----------
    data : DataFrame
        a DataFrame containg the raw acceleration data
    sample_freq : int
        the sampling frequency in which the data was recorded

    Returns
    -------
    data : DataFrame
        the raw acceleration data plus a new column holding the activity labels
    """

    # Detect non-wear time
    data.loc[:, "Non Wear Time"] = detect_non_wear_time_syed2021(data, sample_freq)

    # Detect sleep episodes
    data.loc[:, "Time in bed"] = detect_sleep_triaxial_weitz2022(data, sample_freq)[:len(data)]

    # Classify moderate-to-vigorous and sedentary behavior
    data.loc[:, ["MVPA", "SB"]] = calculate_pa_levels(data, sample_freq)

    # Merge the activity columns into one labelled column. columns indicates the
    # importance of the columns, later names are more important and will be kept
    data.loc[:, "Activity"] = create_activity_column(data, columns=["SB", "MVPA", "Time in bed", "Non Wear Time"])

    # Remove the other columns after merging
    return data[["X", "Y", "Z", "Activity"]]


def summary(data, sample_freq):
    """
    Create a daily summary of the DataFrame

    Parameters
    ----------
    data : DataFrame
        a DataFrame containg the raw acceleration data
    sample_freq : int
        the sampling frequency in which the data was recorded
    level : str
        a string indicating to which level the data should be aggregated

    Returns
    -------
    agg : DataFrame
        the aggregated data holding the minutes spend in each activity
    """
    return pd.get_dummies(data["Activity"]).resample("D").sum() / (sample_freq * 60)