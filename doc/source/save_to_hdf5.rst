Saving multiple gt3x files to hdf5
==================================

Most of the times you have multiple GT3X files you want to analyze. In this case
it is often easier to process all files first and save them as one hdf5 file.
The `Hierarchical Data Format (HDF5) <https://www.hdfgroup.org/solutions/hdf5>`_
is a file format specifically designed to handle large amounts of data. When you
process GT3X files, especially if they contain multi-day recordings, it takes a
considerable amount of time to read these files due to their binary nature. HDF5
significantly reduces data loading time, but only makes sense if the data is used
frequently. In the case only one analysis is performed it might be quicker to
analyze the data directly.

One option is to use the `Pandas <https://pandas.pydata.org/>`_ library to
handle the data. Using pandas has multiple advantages: Pandas has become the
defacto standard for data processing and analysis in Python. It offers a lot of
functionality and has a great community. For most real-life problems solutions
can easily be found on the web and it works amazingly well together with plotting
libraries like Matplotlib and Seaborn. 

.. code-block:: python

    import pandas as pd
    import h5py
    import paat

    hdf5_file_path = 'path/to/hdf5/file'
    files = ['path/to/file1.gt3x', 'path/to/file2.gt3x', ...]

    # Create new empty h5 file
    h5py.File(hdf5_file_path, 'w').close()

    for file in files:

      # Load the data
      time, acceleration, meta = paat.io.read_gt3x(file, rescale=True)

      # Create pandas DataFrame
      data = pd.DataFrame(acceleration, columns=['Y', 'X', 'Z'], index=time)

      # Save data to HDF5 file
      data.to_hdf(hdf5_file, key=meta["Subject_Name"])
