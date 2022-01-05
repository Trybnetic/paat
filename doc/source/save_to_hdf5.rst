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

Here we show some code snippets that can be used to generate a HDF5 file from
multiple GT3X files. Feel free to adapt them as required. All code snippets
assume ``hdf5_file_path`` to be the file path on your hard drive where the final
HDF5 file should be stored and ``files`` to be a list of GT3X files that should
be processed.

Saving with PAAT
----------------

.. code-block:: python

    import h5py
    from paat import io

    hdf5_file_path = 'path/to/hdf5/file'
    files = ['path/to/file1.gt3x', 'path/to/file2.gt3x', ...]

    for file in files:
        time, acceleration, meta = io.read_gt3x(file, rescale=True)

        with h5py.File(hdf5_file_path, 'a') as hdf5_file:
            grp = hdf5_file.create_group(meta["Subject_Name"])
            io.save_dset(grp, "ActiGraph", time, acceleration, meta)


If you have a modern PC with multiple cores, you can also execute the processing
in parallel:

.. code-block:: python

    from multiprocessing import Pool
    import time

    import h5py
    from paat import io

    hdf5_file_path = 'path/to/hdf5/file'
    files = ['path/to/file1.gt3x', 'path/to/file2.gt3x', ...]
    n_jobs = 4

    def process_file(file_path):
        # Load the data
        times, acceleration, meta = paat.io.read_gt3x(file_path, rescale=True)

        # Save data to file
        while True:
            try:
                with h5py.File(HDF5_FILE_PATH, 'a') as hdf5_file:
                    grp = hdf5_file.create_group(meta["Subject_Name"])
                    paat.io.save_dset(grp, "acceleration", times, acceleration, meta)
            # Repeat saving when file is used by a different process
            except OSError:
                time.sleep(random.uniform(0,3))
                continue
            break

      # Create new empty h5 file
      h5py.File(hdf5_file_path, 'w').close()

      # Process all files
      with Pool(n_jobs) as p:
          list(p.imap(process_file, files), total=len(files))



Saving with Pandas
------------------

Another option is to use the `Pandas <https://pandas.pydata.org/>`_ library to
handle the data. Using pandas has multiple advantages: Pandas has become the
defacto standard for data processing and analysis in Python. It offers a lot of
functionality and has a great community. For most real-life problems solutions
can easily be found on the web and it works amazingly well together with plotting
libraries like Matplotlib and Seaborn. However, a huge disadvantage of using the
pandas functionality is that it requires more disk space than using the PAAT
functions.

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
