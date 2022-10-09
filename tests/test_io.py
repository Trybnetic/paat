import os
import tempfile

import numpy as np
import numpy.testing as npt
import pytest
from pygt3x.reader import FileReader

from paat import io, preprocessing


@pytest.fixture
def unscaled_data(file_path):
    acc, _ = io.read_gt3x(file_path, rescale=False, pandas=True)
    return acc


def test_loading_data(file_path, load_gt3x_file):
    data, _ = load_gt3x_file
    _, acceleration, _ = io.read_gt3x(file_path, rescale=True, pandas=False)

    assert np.array_equal(acceleration, data[["Y", "X", "Z"]].values)


@pytest.mark.slow
def test_against_actigraph_implementation(file_path, unscaled_data):
    with FileReader(file_path) as reader:
        ref = reader.to_pandas()

    npt.assert_almost_equal(unscaled_data[["X", "Y", "Z"]].values, ref[["X", "Y", "Z"]].values)


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
