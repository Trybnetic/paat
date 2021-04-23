import os
import tempfile

import numpy as np
import h5py

from paat import io

TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/test_file.gt3x')


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

    assert np.all(time == new_time)
    assert np.all(acceleration == new_acceleration)

    for key, value in meta.items():
        assert meta[key] == new_meta[key]
