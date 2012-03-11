.. _rebot:

Post-processing outputs
-----------------------

`XML output files`_ that are generated during the test execution can be
post-processed afterwards by the :prog:`rebot` tool, which is an integral
part of Robot Framework. It is used automatically when test
reports and logs are generated during the test execution, but there
are also good grounds for using it separately after the execution.

.. contents::
   :depth: 2
   :local:

Using :prog:`rebot` tool
~~~~~~~~~~~~~~~~~~~~~~~~

Synopsis
''''''''

::

    rebot|jyrebot|ipyrebot [options] robot_outputs
    python|jython|ipy -m robot.rebot [options] robot_outputs
    python|jython|ipy path/to/robot/rebot.py [options] robot_outputs
    java -jar robotframework.jar rebot [options] robot_outputs

:prog:`rebot` `runner script`_ runs on Python_ but there are also :prog:`jyrebot`
and :prog:`ipyrebot` `runner scripts`_ that run on Jython_ and IronPython_, respectively.
Using :prog:`rebot` is recommended when it is available because it is considerable
faster than the alternatives. In addition to using these scripts, it is possible to use
:prog:`robot.rebot` `entry point`_ either as a module or a script using
any interpreter, or use the `standalone JAR distribution`_.

Specifying options and arguments
''''''''''''''''''''''''''''''''

The basic syntax for using :prog:`rebot` is exactly the same as when
`starting test execution`_ and also most of the command line options are
identical. The main difference is that arguments to :prog:`rebot` are
`XML output files`_ instead of test data files or directories.

Return codes with :prog:`rebot`
'''''''''''''''''''''''''''''''

Return codes from :prog:`rebot` are exactly same as when `running tests`__.

__ `Return codes`_

Creating different reports and logs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use :prog:`rebot` for creating the same reports and logs that
are created automatically during the test execution. Of course, it is
not sensible to create the exactly same files, but, for example,
having one report with all test cases and another with only some
subset of tests can be useful::

   rebot output.xml
   rebot path/to/output_file.xml
   rebot --include smoke --name Smoke_Tests c:\results\output.xml

Another common usage is creating only the output file when running tests
(log and report generation can be disabled with options :opt:`--log NONE`
and :opt:`--report NONE`) and generating logs and reports later. Tests can,
for example, be executed on different environments, output files collected
to a central place, and reports and logs created there. This approach can
also work very well if generating reports and logs takes a lot of time when
running tests on Jython. Disabling log and report generation and generating
them later with :prog:`rebot` can save a lot of time and use less memory.

Combining outputs
~~~~~~~~~~~~~~~~~

The most important feature of :prog:`rebot` is its ability to combine
outputs from different test execution rounds. This capability allows,
for example, running the same test cases on different environments and
generating an overall report from all outputs. Combining outputs is
extremely easy, all that needs to be done is giving several output
files as arguments::

   rebot output1.xml output2.xml
   rebot outputs/*.xml

When outputs are combined, a new top-level test suite is created so
that test suites in the given output files are its child suites. This
works the same way when `multiple test data files or directories are
executed`__, and also in this case the name of the top-level test
suite is created by joining child suite names with an ampersand (&)
and spaces. These automatically generated names are not that good, and
it is often a good idea to use :opt:`--name` to give a more
meaningful name::

   rebot --name Browser_Compatibility firefox.xml opera.xml safari.xml ie.xml
   rebot --include smoke --name Smoke_Tests c:\results\*.xml

__ `Specifying test data to be executed`_

