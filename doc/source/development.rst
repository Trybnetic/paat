Development
===========

Getting Involved
----------------

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


Workflow
--------

1. Fork this repository on Github. From here on we assume you successfully
   forked this repository to https://github.com/yourname/paat.git

2. Get a local copy of your fork and install the package in 'development'
   mode, which will make changes in the source code active immediately, by running

   .. code:: bash

       git clone https://github.com/yourname/paat.git
       cd paat
       python setup.py develop --user

3. Add code, tests or documentation.

4. Test your changes locally by running within the root folder (``paat/``)

   .. code:: bash

       make checkstyle
       make test

5. Add and commit your changes after tests run through without complaints.

   .. code:: bash

       git add -u
       git commit -m 'fixes #42 by posing the question in the right way'

   You can reference relevant issues in commit messages (like #42) to make GitHub
   link issues and commits together, and with phrase like "fixes #42" you can
   even close relevant issues automatically.

6. Push your local changes to your fork:

   .. code:: bash

       git push git@github.com:yourname/paat.git

7. Open the Pull Requests page at https://github.com/yourname/paat/pulls and
   click "New pull request" to submit your Pull Request to
   https://github.com/quantling/paat.

.. note::

    If you want to develop *paat* you should have installed:

    .. code:: bash

        pip install --user tox pylint pytest pycodestyle sphinx


Running tests
-------------

We use ``make`` and ``tox`` to manage testing. You can run the tests by
executing the following within the repository's root folder (``paat/``):

.. code:: bash

    make test

For manually checking coding guidelines run:

.. code:: bash

    make checkstyle

There is an additional way to invoke ``pylint`` as a linter with tox by running

.. code:: bash

    tox -e lint

The linting gives still a lot of complaints that need some decisions on how to
fix them appropriately.


Building documentation
----------------------

Building the documentation requires some extra dependencies. Therefore, run

.. code:: bash

    pip install -e .[docs]

in the project root directory. This command will install all required
dependencies. The projects documentation is stored in the ``paat/doc/`` folder
and is created with ``sphinx``. You can rebuild the documentation by either
executing

.. code:: bash

   make documentation

in the repository's root folder (``paat``) or by executing

.. code:: bash

   make html

in the documentation folder (``paat/doc/``).


Licensing
---------

All contributions to this project are licensed under the `MIT license
<https://github.com/trybnetic/paat/blob/master/LICENSE.txt>`_. Exceptions are
explicitly marked.
All contributions will be made available under MIT license if no explicit
request for another license is made and agreed on.
