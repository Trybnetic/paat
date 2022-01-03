import os
import tempfile

import numpy as np
import h5py
import pytest

from paat import io, preprocessing

TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/10min_recording.gt3x')


def test_hdf5():
    time, acceleration, meta = io.read_gt3x(FILE_PATH_SIMPLE)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file_path = os.path.join(tmp_dir, "test.hdf5")
        grp_name = meta["Subject_Name"]
        with h5py.File(tmp_file_path, 'a') as hdf5_file:
            grp = hdf5_file.create_group(grp_name)
            io.save_dset(grp, "acceleration", time, acceleration, meta)

        with h5py.File(tmp_file_path, 'r') as hdf5_file:
            grp = hdf5_file[grp_name]
            new_time, new_acceleration, new_meta = io.load_dset(grp, "acceleration")

            new_time, scaled_acceleration, new_meta = io.load_dset(grp, "acceleration", rescale=True)

    assert np.array_equal(time, new_time)
    assert np.array_equal(acceleration, new_acceleration)

    for key, value in meta.items():
        assert meta[key] == new_meta[key]

    # Test whether rescaled data on load is properly rescaled
    new_scaled_acceleration = preprocessing.rescale(new_acceleration,
                                                    acceleration_scale=meta['Acceleration_Scale'])

    assert np.array_equal(scaled_acceleration, new_scaled_acceleration)


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
