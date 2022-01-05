import os
import pickle

import numpy as np
import pytest

from paat import io, wear_time


TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/nwt_recording.gt3x')


@pytest.fixture
def testing_data():
    return io.read_gt3x(FILE_PATH_SIMPLE, rescale=True)


def test_detect_non_wear_time_syed2021(testing_data):
    time, acceleration, meta = testing_data

    nw_vector = wear_time.detect_non_wear_time_syed2021(acceleration,
                                                        meta['Sample_Rate'])

    nw_vector_ref = pickle.load(open(os.path.join(TEST_ROOT, "resources/nw_vector.pkl"), "rb"))

    assert np.array_equal(nw_vector, nw_vector_ref)


def test_detect_non_wear_time_hees2011(testing_data):
    time, acceleration, meta = testing_data

    nw_vector = wear_time.detect_non_wear_time_hees2011(acceleration,
                                                        meta['Sample_Rate'])


def test_detect_non_wear_time_naive(testing_data):
    time, acceleration, meta = testing_data

    std_threshold = 0.004
    min_interval = 60

    nw_vector = wear_time.detect_non_wear_time_naive(acceleration, meta['Sample_Rate'],
                                                     std_threshold, min_interval)
