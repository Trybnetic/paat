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
    ...     io.save_dset(grp, "acceleration", time, acceleration, meta)


and from there be loaded again

.. code-block:: python

    >>> with h5py.File('path/hdf5/file', 'r') as hdf5_file:
    ...     time, acceleration, meta = io.load_dset(grp, "acceleration")


.. note::

    Loading data from a hdf5 file is much faster than loading the data
    from the gt3x files every time. We therefore strongly recommend to process
    all gt3x files in a first step and after that only use hdf5 to access the
    data.


Preprocessing
-------------

In the previous step, we saw different ways to load and store data. As pointed out,
we strongly recommend to process all data first and save them into one hdf5 file.
When you load the data from the gt3x files, this data is not scale to gravitational
units g on default. When working with the original files, you have the option to
set `rescale=True` in :meth:`paat.io.read_gt3x`. We do not recommend rescaling the
data before saving it to the hdf5 file as the rescaled data takes a lot more space
on the disk. Therefore, it is easier to rescale the data after loading:

.. code-block:: python

    >>> from paat import preprocessing
    >>> acceleration = preprocessing.rescale(acceleration,
    ...                                      acceleration_scale=meta['Acceleration_Scale'])

Please note, that rescaling the data is required for all functions for further
processing.


Detect non-wear periods
-----------------------

Different methods to infer non-wear time from the raw acceleration signal are
implemented in the :mod:`paat.wear_time` module. We suggest to use
:meth:`paat.wear_time.detect_non_wear_time_syed2021` as described in [...] as until know this
algorithm has shown the most accurate
estimates for hip-worn ActiGraph acceleration.

.. code-block:: python

    >>> from paat import wear_time
    >>> nw_vector = wear_time.detect_non_wear_time_syed2021(acceleration,
    ...                                                     hz=meta['Sample_Rate'])

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
