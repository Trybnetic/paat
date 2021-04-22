Examples
========

Save a whole batch of gt3x files to hdf5
----------------------------------------

.. code-block:: python

    import h5py
    from paat import io

    hdf5_file_path = 'path/to/hdf5/file'
    files = ['path/to/file1.gt3x', 'path/to/file2.gt3x', ...]

    for file in files:
        time, acceleration, meta = io.read_gt3x(file)

        with h5py.File(hdf5_file_path, 'a') as hdf5_file:
            grp = hdf5_file.create_group(meta["Subject_Name"])
            io.save_dset(grp, "ActiGraph", time, acceleration, meta)
