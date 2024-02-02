.. automodule:: paat
  :noindex:


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contents

   background
   examples
   paat
   development
   credits


Quickstart
----------

Installation
~~~~~~~~~~~~

At the moment, the easiest way to install *paat* directly from GitHub by running:

.. code:: bash

    pip install git+https://github.com/Trybnetic/paat.git


Usage
~~~~~

For now, several functions to work with raw data from ActiGraph devices are
implemented while others are still work in progress. The following code snippet
should give you a brief overview and idea on how to use this package. Further
examples and more information on the functions can be found in the documentation.

.. code-block:: python

    # Load data from file
    data, sample_freq = paat.read_gt3x('path/to/gt3x/file')

    # Detect non-wear time
    data.loc[:, "Non Wear Time"] = paat.detect_non_wear_time_syed2021(data, sample_freq)

    # Detect sleep episodes
    data.loc[:, "Sleep"] = paat.detect_sleep_weitz2022(data, sample_freq)

    # Classify moderate-to-vigorous and sedentary behavior
    data.loc[:, ["MVPA", "SB"]] = paat.calculate_pa_levels(data, sample_freq)

    # Merge the activity columns into one labelled column. columns indicates the
    # importance of the columns, later names are more important and will be kept
    data.loc[:, "Activity"] = paat.create_activity_column(data, columns=["SB", "MVPA", "Sleep", "Non Wear Time"])

    # Remove the other columns after merging
    data =  data[["X", "Y", "Z", "Activity"]]

.. note::

    In this example, methods of `Syed et al. (2021) <https://doi.org/10.1038/s41598-021-87757-z>`_
    and `Weitz et al. (2022) <https://www.medrxiv.org/content/10.1101/2022.03.07.22270992>`_ and activity
    thresholds of `Sanders et al. (2019) <https://doi.org/10.1080/02640414.2018.1555904>`_.
    However, these are only examples. There are multiple methods implemented in PAAT
    and the processing pipeline can easily be adjusted to individual needs. More examples
    can be found in the examples section.
