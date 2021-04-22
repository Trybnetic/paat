import os
import pickle

import numpy as np

from paat import io, wear_time


TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/test_file.gt3x')


def test_non_wear_time_algorithm():
    time, acceleration, meta = io.read_gt3x(FILE_PATH_SIMPLE)

    nw_vector, nw_data = wear_time.cnn_nw_algorithm(raw_acc = acceleration,
                									hz = int(meta['Sample_Rate']))

    nw_vector_ref = pickle.load(open(os.path.join(TEST_ROOT, "resources/nw_vector.pkl"), "rb"))
    nw_data_ref = pickle.load(open(os.path.join(TEST_ROOT, "resources/nw_data.pkl"), "rb"))

    assert np.all(nw_vector == nw_vector_ref)
    assert np.all(nw_data == nw_data_ref)
