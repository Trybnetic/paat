Quickstart
==========

Installation
------------

First, you need to install *paat*. The easiest way to do this is using
`pip <https://pip.pypa.io/en/stable/>`_:

.. code:: bash

    pip install --user paat


Usage
-----

For now, several functions to work with raw data from ActiGraph devices are
implemented while others are still work in progress. The following code snippet
should give you a brief overview and idea on how to use this package. Further
examples and more information on the functions can be found in the documentation.

.. code-block:: python

    import paat

    # Load data from file
    time, acceleration, meta = paat.io.read_gt3x('path/to/gt3x/file', rescale=True)

    # Detect non-wear time
    nw_vector = paat.wear_time.detect_non_wear_time_syed2021(acceleration, meta['Sample_Rate'])

    # Detect sleep episodes
    sleep_vector = paat.sleep.detect_sleep_weitz2022(time, acceleration)

    # Classify moderate-to-vigorous and sedentary behavior
    mvpa_vector, sedentary_vector = paat.estimates.calculate_pa_levels(time, acceleration,
                                                                       mvpa_cutpoint=.069,
                                                                       sb_cutpoint=.015,
                                                                       interval="1s")


For a more detailed description of the workflow see our examples on how to analyze
data.
