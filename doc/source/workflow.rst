Workflow
========


Load data from GT3X file
------------------------

To load data from a gt3x file, the :meth:`paat.io.read_gt3x` function is implemented in
the :mod:`paat.io` module.

.. code-block:: python

    >>> from paat import io
    >>> time, acceleration, meta = io.read_gt3x('path/to/gt3x/file')


Store data in hdf5 file format
------------------------------

Data can easily be saved to a HDF5 file

.. code-block:: python

    >>> import h5py
    >>> with h5py.File('path/hdf5/file', 'a') as hdf5_file:
    ...     grp = hdf5_file.create_group(meta["Subject_Name"])
    ...     io.save_dset(grp, "ActiGraph", time, acceleration, meta)


and from there be loaded again

.. code-block:: python

    >>> with h5py.File('path/hdf5/file', 'r') as hdf5_file:
    ...     time, acceleration, meta = io.load_dset(grp, "ActiGraph")


.. note::

    Loading data from a hdf5 file is much faster than loading the data
    from the gt3x files every time. We therefore strongly recommend to process
    all gt3x files in a first step and after that only use hdf5 to access the
    data.


Detect non-wear periods
-----------------------

Different methods to infer non-wear time from the raw acceleration signal are
implemented in the :mod:`paat.wear_time` module. We suggest to use
:meth:`paat.wear_time.detect_non_wear_time_syed2021` as described in [...] as until know this
algorithm has shown the most accurate
estimates for hip-worn ActiGraph acceleration.

.. code-block:: python

    >>> from paat import wear_time
    >>> nw_vector, nw_data = wear_time.detect_non_wear_time_syed2021(acceleration,
    ...                                                              hz=meta['Sample_Rate'])

But there are also other non-wear time algorithm implemented in the :mod:`paat.wear_time`
module. For wrist-worn accelerometer data, the method developed by [...] might be more
appropriate and is implemented in :meth:`paat.wear_time.detect_non_wear_time_hees2013`:

.. code-block:: python

    >>> from paat import wear_time
    >>> nw_vector = wear_time.detect_non_wear_time_hees2013(acceleration,
    ...                                                     hz=meta['Sample_Rate'])


Detect sleep periods
--------------------


Detect activity periods
-----------------------


Calculate summary statistics
----------------------------
