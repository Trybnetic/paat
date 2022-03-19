=========================================
Physical Activity Analysis Toolbox (PAAT)
=========================================

    **Note:** This package is currently work in progress and the API might change
    anytime!

The physical activity analysis toolbox (PAAT) is a comprehensive toolbox to
analyze raw acceleration data. We developed all code mainly for analyzing
ActiGraph data (GT3X files) in large sample study settings where manual annotation
and analysis is not feasible. Most functions come along with scientific papers
describing the methodology in detail. Even though, the package was and is primarily
develop for analyzing ActiGraph data, we warmly welcome contributions for other
clinical sensors as well!


Installation
============

At the moment, the easiest way to install *paat* directly from GitHub by running:

.. code:: bash

    pip install git+https://github.com/Trybnetic/paat.git


Usage
=====

For now, several functions to work with raw data from ActiGraph devices are
implemented while others are still work in progress. The following code snippet
should give you a brief overview and idea on how to use this package. Further
examples and more information on the functions can be found in the documentation.

.. code-block:: python

    # Load data from file
    data, sample_freq = paat.read_gt3x(FILE_PATH_SIMPLE)

    # Detect non-wear time
    data.loc[:, "Non Wear Time"] = paat.detect_non_wear_time_syed2021(data, sample_freq)

    # Detect sleep episodes
    data.loc[:, "Sleep"] = paat.detect_sleep_weitz2022(data, sample_freq)

    # Classify moderate-to-vigorous and sedentary behavior
    data.loc[:, ["MVPA", "SB"]] = paat.calculate_pa_levels(data, sample_freq)

    data.loc[:, "Activity"] = paat.create_activity_column(data, columns=["Non Wear Time", "Sleep", "MVPA", "SB"])

    data =  data[["X", "Y", "Z", "Activity"]]



Getting involved
================

The *paat* project welcomes help in the following ways:

* Making Pull Requests for
  `code <https://github.com/trybnetic/paat/tree/master/paat>`_,
  `tests <https://github.com/trybnetic/paat/tree/master/tests>`_
  or `documentation <https://github.com/trybnetic/paat/tree/master/doc>`_.
* Commenting on `open issues <https://github.com/trybnetic/paat/issues>`_
  and `pull requests <https://github.com/trybnetic/paat/pulls>`_.
* Helping to answer `questions in the issue section
  <https://github.com/trybnetic/paat/labels/question>`_.
* Creating feature requests or adding bug reports in the `issue section
  <https://github.com/trybnetic/paat/issues/new>`_.


Authors and Contributers
========================

*paat* was mainly developed by
`Marc Weitz <https://github.com/trybnetic>`_
and `Shaheen Syed <https://github.com/shaheen-syed/>`_. For the full list of
contributors have a look at `Github's Contributor summary
<https://github.com/trybnetic/paat/contributors>`_.

Currently, it is maintained by `Marc Weitz <https://github.com/trybnetic>`_. In case
you want to contact the project maintainers, please send an email to
marc [dot] weitz [at] uit [dot] no


Acknowledgments
===============

This work was supported by the High North Population Studies at UiT The Arctic
University of Norway.
