Saving multiple gt3x files to hdf5
==================================

Most of the times you have multiple GT3X files you want to analyze. In this case
it is often easier to process all files first and save them as one hdf5 file.
The `Hierarchical Data Format (HDF5) <https://www.hdfgroup.org/solutions/hdf5>`_
is a file format specifically designed to handle large amounts of data. When you
process GT3X files, especially if they contain multi-day recordings, it takes a
considerable amount of time to read these files due to their binary nature. HDF5
significantly reduces data loading time, but only makes sense if the data is used
multiple times. In the case only one analysis is performed it might be quicker to
analyze the data directly.

The following example illustrates how to create a HDF5 file from a list of GT3X
files. If you don't know how to get this list have a look at the
`Read GT3X Files with PAAT` tutorial.

.. code-block:: python

    import h5py
    import paat

    hdf5_file_path = 'path/to/hdf5/file'
    files = ['path/to/file1.gt3x', 'path/to/file2.gt3x', ...]

    # Create new empty h5 file
    h5py.File(hdf5_file_path, 'w').close()

    for file in files:

      # Load the data
      data, sample_freq = paat.read_gt3x(file)

      # Save data to HDF5 file
      data.to_hdf(hdf5_file, key=file)
