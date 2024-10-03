=========================================
Physical Activity Analysis Toolbox (PAAT)
=========================================

    **Note:** This package is currently under development and the API might change
    anytime! For reproducible versions, see `zenodo <https://doi.org/10.5281/zenodo.13885706>`_.


.. image:: https://github.com/Trybnetic/paat/actions/workflows/python-test.yml/badge.svg
 :target: https://github.com/Trybnetic/paat/actions/workflows/python-test.yml
 :alt: Tests

.. image:: https://codecov.io/gh/Trybnetic/paat/branch/main/graph/badge.svg
  :target: https://codecov.io/gh/Trybnetic/paat
  :alt: Coverage

.. image:: https://readthedocs.org/projects/paat/badge/?version=latest
 :target: https://paat.readthedocs.io/en/latest/?badge=latest
 :alt: Documentation Status

.. image:: https://img.shields.io/github/license/trybnetic/paat.svg
 :target: https://github.com/trybnetic/paat/blob/master/LICENSE.txt
 :alt: License

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.13885749.svg
  :target: https://doi.org/10.5281/zenodo.13885749
  :alt: zenodo

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

    pip install paat


Usage
=====

For now, several functions to work with raw data from ActiGraph devices are
implemented while others are still work in progress. The following code snippet
should give you a brief overview and idea on how to use this package. Further
examples and more information on the functions can be found in the documentation.

.. code-block:: python

    # Load data from file
    data, sample_freq = paat.read_gt3x('path/to/gt3x/file')

    # Detect non-wear time
    data.loc[:, "Non Wear Time"] = paat.detect_non_wear_time_hees2011(data, sample_freq)

    # Detect sleep episodes
    data.loc[:, "Time in Bed"] = paat.detect_time_in_bed_weitz2024(data, sample_freq)

    # Classify moderate-to-vigorous and sedentary behavior
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
