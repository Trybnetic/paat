import os
import tempfile

import numpy as np
import numpy.testing as npt
import pytest
from pygt3x.reader import FileReader
from pygt3x.calibrated_reader import CalibratedReader

from paat import io, preprocessing

TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/10min_recording.gt3x')

@pytest.fixture
def data():
    return io.read_gt3x(FILE_PATH_SIMPLE, rescale=True, pandas=True)


@pytest.fixture
def unscaled_data():
    return io.read_gt3x(FILE_PATH_SIMPLE, rescale=False, pandas=True)


def test_loading_data(data):
    _, acceleration, _ = io.read_gt3x(FILE_PATH_SIMPLE, rescale=True)

    assert np.array_equal(acceleration, data[["Y", "X", "Z"]].values)


@pytest.mark.slow
def test_against_actigraph_implementation(unscaled_data):
    with FileReader(FILE_PATH_SIMPLE) as reader:
        ref = reader.to_pandas()

    npt.assert_almost_equal(unscaled_data[["X", "Y", "Z"]].values, ref[["X", "Y", "Z"]].values)
    #assert np.allclose(data[["X", "Y", "Z"]].values, ref[["X", "Y", "Z"]].values)


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
