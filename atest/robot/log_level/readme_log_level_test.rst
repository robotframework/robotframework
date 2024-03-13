The "log level 'USER'" feature
==============================

The bunch of log levels provided by the Robot Framework, has been extended by a log level ``USER``, that is
placed between ``INFO`` and ``WARN``.

The reason for this new log level is to have a better separation between user specific log messages
and standard messages provided by the Robot Framework itself (at default log level ``INFO``).
A user who really wants to have his own output only, has the ability now to switch to log level ``USER``,
at which all ``INFO`` messages (and messages below ``INFO``) from Robot Framework or other sources like Python
keyword libraries or resource files are suppressed.

This reduces the amount of content in Robot Framework output files. 

Further output like the start and the end of a keyword execution, the start and the end of loops and IF conditions
have been made log level dependent (``debugfile.py`` and ``xmllogger.py``) - with default level ``INFO``.
Therefore in all levels above ``INFO`` those messages are not present in output files any more.

Also this measure reduces the amount of content in Robot Framework output files and eases the readability.


The "log level" self test
=========================

A robot file, a resource file and a Python keyword library file contain ``Log`` keyword calls for every available log level.

At first the robot file executes his own ``Log`` keywords, after this the robot file executes the keyword defined in the
resource file (the keyword that contains the ``Log`` keyword calls for every available log level) and then the corresponding
keyword defined in the Python keyword library file.

The robot file itself is called by another robot file with every available log level in command line.

For every combination of log levels it is checked if all expected log messages can be found in the debug log file
and in the XML output file. Additionally it is checked if all declined log messages are not present in these files.

To check also the remaining content like the start and the end of a keyword execution or ``FOR`` loops and ``IF`` conditions,
an output file comparison follows. The current output file is compared with a reference file, that is a previous output
file with manually checked content that is like expected. Not the entire content is compared. The comparison is reduced
to a subset of content based on a pattern file for the debug log file in text format (``log_level_pattern_DEBUG_LOG.txt``)
and a pattern file for the XML output file (``log_level_pattern_XML.txt``).

Every deviation immediately stops the test.

The log files of this "log level" self test can be found in a separate output folder ``log_level_logfiles``
that is a sub folder of the output folder defined by the Robot Framework atest script ``run.py``.

The test files of the "log level" self test are placed in ``atest\robot\log_level``.


Message string structure
------------------------

Every message written by the self test, has the following structure:

.. code:: python

   === [<unique identifier>] - [<origin>] - [<log level>]: <test string>

Example:

.. code:: python

   === [LOG_LEVEL_TEST] - [ROBOT_FILE] - [ERROR]: "ERROR test string ERROR test string ERROR test string ERROR"

* ``<unique identifier>``

  The ``<unique identifier>`` is ``LOG_LEVEL_TEST``. Every line contains this string.

* ``<origin>``

  ``<origin>`` is one of (``ROBOT_FILE``, ``RESOURCE_FILE``, ``PYTHON_LIBRARY``) and belongs to the position of the ``Log`` keyword
  that produces this this line of output.

* ``<log level>``

  ``<log level>`` is the log level, the message belongs to.

* ``<test string>``

  ``<test string>`` is a simple test string with some dummy content and contains also the log level.

With this naming convention every self test log message is individual and therefore can be detected in output files easily.


Self test files
---------------

* ``log_level.robot``

  Contains ``Log`` keyword calls for all available log levels and the keyword calls from resource file and Python keyword library.

* ``log_level_addons/log_level.resource``

  Contains ``Log`` keyword calls for all available log levels

* ``log_level_addons/log_level.py``

  Contains ``Log`` keyword calls for all available log levels

* ``log_level_trigger.robot``

  Executes ``log_level.robot`` with all available log levels and checks the resulting output files.

* ``libs/ClogLevelTest.py``

  Keyword library to support the self test. Responsible for:

  - versioning
  - definition of all output files and folders belonging to the self test
  - execution of ``log_level.robot``
  - check of output (log messages in output files)

* ``libs/CLogData.py``

  Pure Python module to define and manage the log message strings used by the self test.
  Background is to have the log message strings defined at one single position only.

  The log message strings defined in this module, are used twice: as ``Log`` keyword parameter
  and also as string to search for in output files.

* ``libs/CComparison.py``

  Pure Python module containing the file comparison mechanism.

* ``referencelogfiles/*.xml``

  Reference files used for output file comparison of XML output files

* ``referencelogfiles/log_level_pattern_DEBUG_LOG.txt``

  Pattern file with regular expressions used for debug log file comparison

* ``referencelogfiles/log_level_pattern_XML.txt``

  Pattern file with regular expressions used for XML output file comparison

* ``robotframework\atest\robot\log_level\readme_log_level_test.rst``

  The feature and self test documentation (this readme)


Self test execution
-------------------

.. code:: python

   <Python interpreter> "./atest/run.py" -l log_level_test_log.html -r log_level_test_report.html -b log_level_test_debug.log "./atest/robot/log_level"
