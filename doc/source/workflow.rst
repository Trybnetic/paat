Workflow
========


Load data from GT3X file
------------------------

.. code-block:: python

    >>> from paat import io
    >>> time, acceleration, meta = io.read_gt3x('path/to/gt3x/file')


Detect non-wear times
---------------------

.. code-block:: python

    >>> from paat import wear_time
    >>> nw_vector, nw_data = wear_time.cnn_nw_algorithm(raw_acc = actigraph_acc,
    ...             					hz = int(meta_data['Sample_Rate']),
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
