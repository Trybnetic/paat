from .estimates import calculate_pa_levels, create_activity_column
from .sleep import detect_sleep_weitz2022
from .wear_time import etect_non_wear_time_syed2021


def annotate(data, sample_freq):

    # Detect non-wear time
    data.loc[:, "Non Wear Time"] = detect_non_wear_time_syed2021(data, sample_freq)

    # Detect sleep episodes
    data.loc[:, "Time in bed"] = detect_sleep_triaxial_weitz2022(data, sample_freq)[:len(data)]

    # Classify moderate-to-vigorous and sedentary behavior
    data.loc[:, ["MVPA", "SB"]] = calculate_pa_levels(data, sample_freq)

    # Merge the activity columns into one labelled column. columns indicates the
    # importance of the columns, later names are more important and will be kept
    data.loc[:, "Activity"] = create_activity_column(data, columns=["SB", "MVPA", "Time in bed", "Non Wear Time"])

    #data = data.resample("1min").mean()
    
    # Remove the other columns after merging
    return data[["X", "Y", "Z", "Activity"]]
