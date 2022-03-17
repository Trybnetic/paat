import os
import tempfile

import numpy as np
import h5py
import pytest

from paat import io, preprocessing

TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/10min_recording.gt3x')


def test_loading_data():
    _, acceleration, _ = io.read_gt3x(FILE_PATH_SIMPLE, rescale=True)

    data = io.read_gt3x(FILE_PATH_SIMPLE, rescale=True, pandas=True)

    assert np.array_equal(acceleration, data[["Y", "X", "Z"]].values)


def test_exceptions():
    with pytest.raises(NotImplementedError) as e_info:
        time_data = np.arange(10)
        hz = 33
        io._create_time_array(time_data, hz)
        assert e_info

    with pytest.raises(NotImplementedError) as e_info:
        start = np.asarray(np.datetime64('today'), dtype='datetime64[ms]')
        n_samples = 330
        hz = 33
        io._create_time_vector(start, n_samples, hz)
        assert e_info
