=========================================
Physical Activity Analysis Toolbox (PAAT)
=========================================

The physical activity analysis toolbox (PAAT) is a comprehensive toolbox to
analyse raw acceleration data.


Installation
============

For now, the easiest way to install *paat* is to install it in development mode
by running:

.. code:: bash

    git clone https://github.com/trybnetic/paat.git
    cd paat
    python setup.py develop --user

This also enables that all changes you make in the code become active immediately.


Usage
=====


Load data from GT3X file
------------------------

.. code-block:: python

    >>> from paat import io
    >>> time, acceleration, meta = io.read_gt3x('path/to/gt3x/file')


Detect non-wear times
---------------------

.. code-block:: python

    >>> from paat import wear_time
    >>> nw_vector = wear_time.detect_non_wear_time_syed2021(acceleration, hz=meta['Sample_Rate'])


Detect sleep periods
--------------------

Will be implemented soon


Detect activity periods
-----------------------

Will be implemented soon


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
