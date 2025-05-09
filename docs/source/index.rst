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

    pip install paat


Usage
~~~~~

For now, several functions to work with raw data from ActiGraph devices are implemented while others are still work in progress. The following code snippet should give you a brief overview and idea on how to use this package. Further, examples and more information on the functions can be found in the documentation.

It is also possible to use other packages such as `actipy <lhttps://github.com/OxWearables/actipy>`_ or `SciKit Digital Health (SKDH) <https://github.com/pfizer-opensource/scikit-digital-health>`_ to load the data. The only prerequisite is that a pandas DataFrame with a TimeStamp index and the sampling frequency is provided.

.. code-block:: python

    # Load data from file
    data, sample_freq = paat.read_gt3x('path/to/gt3x/file')

    # Detect non-wear time
    data.loc[:, "Non Wear Time"] = paat.detect_non_wear_time_hees2011(data, sample_freq)

    # Detect sleep episodes
    data.loc[:, "Time in Bed"] = paat.detect_time_in_bed_weitz2024(data, sample_freq)

    # Classify moderate-to-vigorous and sedentary behavior using the cutpoints from Sanders et al. (2019)
    data.loc[:, ["MVPA", "SB"]] = paat.calculate_pa_levels(
        data, 
        sample_freq,
        mvpa_cutpoint=.069, 
        sb_cutpoint=.015
    )

    # Merge the activity columns into one labelled column. columns indicates the
    # importance of the columns, later names are more important and will be kept
    data.loc[:, "Activity"] = paat.create_activity_column(
        data, 
        columns=["SB", "MVPA", "Time in Bed", "Non Wear Time"]
    )

    # Remove the other columns after merging
    data =  data[["X", "Y", "Z", "Activity"]]

.. note::

    Note that these are only examples. There are multiple methods implemented in PAAT
    and the processing pipeline can easily be adjusted to individual needs. More (and 
    also interactive) examples can be found in the :doc:`examples section <examples>` 
    and an overview over the implemented methods including references to the original 
    publications is also provided in the :doc:`API documentation <paat>`. 
