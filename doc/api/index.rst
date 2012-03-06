=================================
Robot Framework API documentation
=================================

.. toctree::
   :maxdepth: 2



This document describes the public API of Robot Framework. Installation,
basic usage and wealth of other topics are covered in the `user guide`__.

__ http://code.google.com/p/robotframework/wiki/UserGuide

Logging
=======

.. automodule:: robot.api.logger

API functions
-------------

.. autofunction:: robot.api.logger.warn
.. autofunction:: robot.api.logger.info
.. autofunction:: robot.api.logger.debug
.. autofunction:: robot.api.logger.trace
.. autofunction:: robot.api.logger.console
.. autofunction:: robot.api.logger.write


Parsing
=======

.. automodule:: robot.parsing.model
    :members:
    :inherited-members:


Saving data
===========


.. automodule:: robot.writer
    :members:


.. automodule:: robot.writer.datafilewriter
    :members:

.. autofunction:: robot.writer.datafilewriter.DataFileWriter


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

