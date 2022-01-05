Reading a gt3x file
===================

GT3X is the proprietary file format from ActiGraph. In fact, it is a ZIP archive
containing a meta data text file and a binary data file. To read GT3X files,
the :meth:`paat.io.read_gt3x` function is implemented in the :mod:`paat.io`
module. This function unzips and reads the content of the GT3X file and returns
a time vector, an acceleration matrix and a dictionary of meta data.

.. code-block:: python

    >>> import paat
    >>> time, acceleration, meta = paat.io.read_gt3x('path/to/gt3x/file')


.. note::

    The acceleration values stored in a GT3X file are not saved in gravitational
    units. If you want your acceleration signal in g, you have to rescale the
    values (see :meth:`paat.io.read_gt3x` and :meth:`paat.preprocessing.rescale`)


To rescale the data, you additionally need to run

.. code-block:: python

    >>> acceleration = paat.preprocessing.rescale(acceleration,
    ...                                           acceleration_scale=meta['Acceleration_Scale'])


or already rescale the data upon reading, by setting `rescale=True`

.. code-block:: python

    >>> time, acceleration, meta = paat.io.read_gt3x('path/to/gt3x/file', rescale=True)
