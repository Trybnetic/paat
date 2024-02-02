import os

import pytest
import numpy as np
import paat

TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/10min_recording.gt3x')


def test_simple_example():
    """
    Test the Quickstart/Readme processing pipeline
    """
    # Load data from file
    data, sample_freq = paat.read_gt3x(FILE_PATH_SIMPLE)

    # Annotate the acceleration data
    data = paat.annotate(data, sample_freq)

    # Get ActiLife counts
    counts = paat.calculate_actigraph_counts(data, sample_freq, "10s")
    data.loc[:, ["Y_counts", "X_counts", "Z_counts"]] = counts


def test_advanced_example():
    """
    Test the advanced example from the Readme
    """

    # Load data from file
    data, sample_freq = paat.read_gt3x(FILE_PATH_SIMPLE)

    # Detect non-wear time
    data.loc[:, "Non Wear Time"] = paat.detect_non_wear_time_syed2021(data, sample_freq)

    # Detect sleep episodes
    data.loc[:, "Sleep"] = paat.detect_sleep_weitz2022(data, sample_freq)

    # Classify moderate-to-vigorous and sedentary behavior
    data.loc[:, ["MVPA", "SB"]] = paat.calculate_pa_levels(data, sample_freq)

    # Merge the activity columns into one labelled column. columns indicates the
    # importance of the columns, later names are more important and will be kept
    data.loc[:, "Activity"] = paat.create_activity_column(data, columns=["SB", "MVPA", "Sleep", "Non Wear Time"])

    # Remove the other columns after merging
    data =  data[["X", "Y", "Z", "Activity"]]