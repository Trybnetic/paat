import os

import pytest
import numpy as np
import pandas as pd
import paat

TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/10min_recording.gt3x')
FILE_PATH = os.path.join(TEST_ROOT, 'resources/processed_v1_0_0b8.csv.gz')


def test_pipeline():
    """
    Test the Quickstart/Readme processing pipeline
    """
    # Load data from file
    data, sample_freq = paat.read_gt3x(FILE_PATH_SIMPLE)

    # Detect non-wear time
    data.loc[:, "Non Wear Time"] = paat.detect_non_wear_time_syed2021(data, sample_freq)

    # Detect sleep episodes
    data.loc[:, "Sleep"] = paat.detect_time_in_bed_weitz2024(data, sample_freq)

    # Classify moderate-to-vigorous and sedentary behavior
    data.loc[:, ["MVPA", "SB"]] = paat.calculate_pa_levels(
        data, 
        sample_freq, 
        mvpa_cutpoint=.069, 
        sb_cutpoint=.015
    )

    # Merge the activity columns into one labelled column
    data.loc[:, "Activity"] = paat.create_activity_column(
        data, 
        columns=["Non Wear Time", "Sleep", "MVPA", "SB"]
    )

    # Remove the other columns after merging
    data = data[["X", "Y", "Z", "Activity"]]

    # Get ActiLife counts
    counts = paat.calculate_actigraph_counts(data, sample_freq, "10s")
    data.loc[:, ["Y_counts", "X_counts", "Z_counts"]] = counts


@pytest.mark.slow
def test_against_v1_0_0b8():
    data, sample_freq = pd.read_csv(FILE_PATH, compression="gzip"), 100
    data["Timestamp"] = pd.to_datetime(data["Timestamp"])
    data = data.set_index("Timestamp")

    # Detect non-wear time
    data.loc[:, "Non Wear Time"] = paat.detect_non_wear_time_syed2021(data.loc[:, ["X", "Y", "Z"]], sample_freq)

    # Detect sleep episodes
    data.loc[:, "Sleep"] = paat.detect_time_in_bed_weitz2024(data.loc[:, ["X", "Y", "Z"]], sample_freq)

    # Classify moderate-to-vigorous and sedentary behavior
    data.loc[:, ["MVPA", "SB"]] = paat.calculate_pa_levels(
        data.loc[:, ["X", "Y", "Z"]], 
        sample_freq, 
        mvpa_cutpoint=.069, 
        sb_cutpoint=.015
    )

    # Merge the activity columns into one labelled column
    data.loc[:, "Activity_new"] = paat.create_activity_column(
        data, 
        columns=["Non Wear Time", "Sleep", "MVPA", "SB"]
    )

    # Remove the other columns after merging
    data = data[["X", "Y", "Z", "Activity", "Activity_new"]]

    assert (data["Activity"] == data["Activity_new"]).all()