import os
import pickle

import numpy as np
import pytest

from paat import io, wear_time


@pytest.fixture
def nwt_data(test_root_path):
    file_path = os.path.join(test_root_path, 'resources/nwt_recording.gt3x')
    return io.read_gt3x(file_path, rescale=True, pandas=True)


def test_detect_non_wear_time_syed2021(nwt_data, test_root_path):
    data, sample_freq = nwt_data

    nw_vector = wear_time.detect_non_wear_time_syed2021(data, sample_freq)
    nw_vector = nw_vector[:-100]  # Test reference was created with old version which skipped the last second

    nw_vector_ref = pickle.load(open(os.path.join(test_root_path, "resources/nw_vector.pkl"), "rb"))

    assert np.array_equal(nw_vector, nw_vector_ref)


def test_detect_non_wear_time_hees2011(nwt_data):
    data, sample_freq = nwt_data

    nw_vector = wear_time.detect_non_wear_time_hees2011(data, sample_freq)


def test_detect_non_wear_time_naive(nwt_data):
    data, sample_freq = nwt_data

    std_threshold = 0.004
    min_interval = 60

    nw_vector = wear_time.detect_non_wear_time_naive(data, sample_freq,
                                                     std_threshold, min_interval)
