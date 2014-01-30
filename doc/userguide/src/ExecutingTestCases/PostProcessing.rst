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

Merging re-executed output
~~~~~~~~~~~~~~~~~~~~~~~~~~

There is often a need to re-execute a subset of tests, for example, after
fixing a bug in the system under test or in the tests themselves. This can be
accomplished by `selecting test cases`_ by names (:opt:`--test` and
:opt:`--suite` options), tags (:opt:`--include` and :opt:`--exclude`), or
by previous status (:opt:`--rerunfailed`).

Combining re-execution results with the original results using the default
`combining outputs`_ approach does not work too well. The main problem is
that you get separate test suites and possibly already fixed failures are
also shown. In this situation it is often better to use :opt:`--rerunmerge (-R)`
option to tell :prog:`rebot` to merge the results instead. In practice this
means that tests from the latter test runs replace tests in the original.
The usage is best illustrated by a practical example using :opt:`--rerunfailed`
and :opt:`--rerunmerge` together::

  pybot --output original.xml tests                            # first execute all tests
  pybot --rerunfailed original.xml --output rerun.xml tests    # then re-execute failing
  rebot --rerunmerge original.xml rerun.xml                    # finally merge results

It is also possible to merge together more than two results, and all other
command line options work normally::

  rebot --rerunmerge --name Merged --critical regression original.xml rerun1.xml rerun2.xml

The message of the merged tests contains a note that results have been
replaced. The message also shows the old status and message of the test.

Merging results requires that the original result contains all same suites
and tests as the merged results. Suites and tests tests not found from the
original are ignored and an error printed to the console.

.. note:: Merging re-executed results is a new feature in Robot Framework 2.8.4.
