import os
import tempfile

import numpy as np
import numpy.testing as npt
import pytest
from pygt3x.reader import FileReader

from paat import io, preprocessing


@pytest.fixture
def unscaled_data(file_path):
    return io.read_gt3x(file_path, rescale=False, pandas=True)


def test_loading_data(file_path, load_gt3x_file):
    data, _ = load_gt3x_file
    _, acceleration, _ = io.read_gt3x(file_path, rescale=True, pandas=False)

    assert np.array_equal(acceleration, data[["Y", "X", "Z"]].values)


def test_loading_metadata(file_path):
    meta = io.read_metadata(file_path)
    
    expected = {
        'Acceleration_Max': 8.0,
        'Acceleration_Min': -8.0,
        'Acceleration_Scale': 256.0,
        'Battery_Voltage': '4,17',
        'Board_Revision': 3,
        'Device_Type': 'wGT3XBT',
        'Download_Date': '2022-01-03T10:33:05',
        'Firmware': '1.9.2',
        'Last_Sample_Time': '2022-01-03T10:30:00',
        'Sample_Rate': 100,
        'Serial_Number': 'MOS2C06152277',
        'Start_Date': '2022-01-03T10:20:00',
        'Stop_Date': '2022-01-03T10:30:00',
        'Subject_Name': 'MOS2C06152277',
        'TimeZone': '01:00:00',
        'Unexpected_Resets': 0
    }

    assert meta == expected


@pytest.mark.slow
def test_against_actigraph_implementation(file_path, unscaled_data):
    with FileReader(file_path) as reader:
        ref = reader.to_pandas()

    npt.assert_almost_equal(unscaled_data[["X", "Y", "Z"]].values, ref[["X", "Y", "Z"]].values)
    #assert np.allclose(data[["X", "Y", "Z"]].values, ref[["X", "Y", "Z"]].values)


def test_paat_vs_pygt3x_loading():
    file_path = os.path.join(os.path.pardir, os.path.dirname(__file__), 'resources/10min_recording.gt3x')

    ref, ref_sample_freq = io.read_gt3x(file_path)

    data, sample_freq = io.read_gt3x(file_path, use_pygt3x=True)

    assert np.allclose(data[["X", "Y", "Z"]].values, ref[["X", "Y", "Z"]].values)
    assert ref_sample_freq == sample_freq


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

