import os
import tempfile

import numpy as np
import numpy.testing as npt
import pandas as pd
import h5py
import pytest

from paat import io, features


def test_calculate_actigraph_counts(load_gt3x_file, test_root_path):
    data, sample_freq = load_gt3x_file

    # Test 1sec count processing
    counts_1s = features.calculate_actigraph_counts(data, sample_freq, 1)
    ref_1s = pd.read_csv(os.path.join(test_root_path, 'resources/10min_recording1sec.csv'),
                         skiprows=10, header=None, names=["Y", "X", "Z", "Steps"])

    npt.assert_almost_equal(counts_1s[["X", "Y", "Z"]].values, ref_1s[["X", "Y", "Z"]].values)

    # Test 10sec count processing
    counts_10s = features.calculate_actigraph_counts(data, sample_freq, 10)
    ref_10s = pd.read_csv(os.path.join(test_root_path, 'resources/10min_recording10sec.csv'),
                          skiprows=10, header=None, names=["Y", "X", "Z", "Steps"])

    npt.assert_almost_equal(counts_10s[["X", "Y", "Z"]].values, ref_10s[["X", "Y", "Z"]].values)


def test_calculate_brond_counts(load_gt3x_file):
    data, sample_freq = load_gt3x_file
    brond_counts = features.calculate_brond_counts(data[["Y", "X", "Z"]].values.T, sample_freq, 1)
