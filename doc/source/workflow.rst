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


Detect non-wear times
---------------------

Different methods to infer non-wear time from the raw acceleration signal are
implemented in the :mod:`paat.wear_time` module. We suggest to use
:meth:`paat.wear_time.cnn_nw_algorithm` as described in [...] as until know this
algorithm has shown the most accurate
estimates for hip-worn ActiGraph acceleration.

.. code-block:: python

    >>> from paat import wear_time
    >>>
    >>> # standard deviation threshold in g
  	>>> std_threshold = 0.004
  	>>> # merge distance to group two nearby candidate nonwear episodes
  	>>> distance_in_min = 5
  	>>> # define window length to create input features for the CNN model
  	>>> episode_window_sec = 7
  	>>> # default classification when an episode does not have a starting or stop feature window (happens at t=0 or at the end of the data)
  	>>> edge_true_or_false = True
  	>>> # logical operator to see if both sides need to be classified as non-wear time (AND) or just a single side (OR)
  	>>> start_stop_label_decision = 'and'
    >>>
  	>>> # load cnn model
  	>>> cnn_model_file = os.path.join('cnn_models', f'cnn_v2_{str(episode_window_sec)}.h5')
    >>>
    >>> nw_vector, nw_data = wear_time.cnn_nw_algorithm(raw_acc = acceleration,
    ...             					hz = int(meta['Sample_Rate']),
    ...              					cnn_model_file = cnn_model_file,
    ...              					std_threshold = std_threshold,
    ...              					distance_in_min = distance_in_min,
    ...              					episode_window_sec = episode_window_sec,
    ...              					edge_true_or_false = edge_true_or_false,
    ...              					start_stop_label_decision = start_stop_label_decision)


Detect sleep periods
--------------------


Detect activity periods
-----------------------


Calculate summary statistics
----------------------------
