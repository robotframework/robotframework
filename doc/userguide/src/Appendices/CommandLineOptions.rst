All command line options
========================

This appendix lists all the command line options that are available
when `executing test cases`__ with ``pybot`` or ``jybot``, and when
`post-processing outputs`_ with ``rebot``.

__ `Starting test execution`_

.. contents::
   :depth: 2
   :local:

Command line options for test execution
---------------------------------------

  -N, --name <name>       `Sets the name`_ of the top-level test suite.
  -D, --doc <document>    `Sets the documentation`_ of the top-level test suite.
  -M, --metadata <name:value>  `Sets free metadata`_ for the top level test suite.
  -G, --settag <tag>      `Sets the tag(s)`_ to all executed test cases.
  -t, --test <name>       `Selects the test cases by name`_.
  -s, --suite <name>      `Selects the test suites`_ by name.
  -R, --rerunfailed <file>  `Selects failed tests`_ from an earlier `output file`_ to be re-executed.
  --runfailed <file>      Deprecated since Robot Framework 2.8.4.
                          Use :option:`--rerunfailed` instead.
  -i, --include <tag>     `Selects the test cases`_ by tag.
  -e, --exclude <tag>     `Selects the test cases`_ by tag.
  -c, --critical <tag>    Tests that have the given tag are `considered critical`_.
  -n, --noncritical <tag>  Tests that have the given tag are `not critical`_.
  -v, --variable <name:value>   Sets `individual variables`_.
  -V, --variablefile <path:args>  Sets variables using `variable files`_.
  -d, --outputdir <dir>   Defines where to `create output files`_.
  -o, --output <file>     Sets the path to the generated `output file`_.
  -l, --log <file>        Sets the path to the generated `log file`_.
  -r, --report <file>     Sets the path to the generated `report file`_.
  -x, --xunit <file>      Sets the path to the generated `xUnit compatible result file`_.
  --xunitskipnoncritical  Mark non-critical tests on `xUnit compatible result file`_ as skipped.
  -b, --debugfile <file>  A `debug file`_ that is written during execution.
  -T, --timestampoutputs  `Adds a timestamp`_ to all output files.
  --splitlog              `Split log file`_ into smaller pieces that open in
                          browser transparently.
  --logtitle <title>      `Sets a title`_ for the generated test log.
  --reporttitle <title>   `Sets a title`_ for the generated test report.
  --reportbackground <colors>  `Sets background colors`_ of the generated report.
  -L, --loglevel <level>  `Sets the threshold level`_ for logging. Optionally
                          the default `visible log level`_ can be given
                          separated with a colon (:).
  --suitestatlevel <level>  Defines how many `levels to show`_ in the
                           *Statistics by Suite* table in outputs.
  --tagstatinclude <tag>  `Includes only these tags`_ in the *Statistics by Tag* table.
  --tagstatexclude <tag>  `Excludes these tags`_ from the *Statistics by Tag* table.
  --tagstatcombine <tags:title>  Creates `combined statistics based on tags`_.
  --tagdoc <pattern:doc>  Adds `documentation to the specified tags`_.
  --tagstatlink <pattern:link:title>  Adds `external links`_ to the *Statistics by Tag* table.
  --removekeywords <all|passed|name:pattern|tag:pattern|for|wuks>  `Removes keyword data`_
                          from the generated log file.
  --flattenkeywords <for|foritem|name:pattern|tag:pattern>  `Flattens keywords`_
                          in the generated log file.
  --listener <name:args>  `Sets a listener`_ for monitoring test execution.
  --warnonskippedfiles    Show a warning when `an invalid file is skipped`_.
  --nostatusrc            Sets the `return code`_ to zero regardless of failures
                          in test cases. Error codes are returned normally.
  --runemptysuite         Executes tests also if the selected `test suites are empty`_.
  --dryrun                In the `dry run`_ mode tests are run without executing
                          keywords originating from test libraries. Useful for
                          validating test data syntax.
  --exitonfailure         `Stops test execution <Stopping when first test case fails_>`__
                          if any critical test fails.
  --exitonerror           `Stops test execution <Stopping on parsing or execution error_>`__
                          if any error occurs when parsing test data, importing libraries, and so on.
  --skipteardownonexit    `Skips teardowns`_ is test execution is prematurely stopped.
  --prerunmodifier <name:args>    Activate `programmatic modification of test data`_.
  --prerebotmodifier <name:args>  Activate `programmatic modification of results`_.
  --randomize <all|suites|tests|none>  `Randomizes`_ test execution order.
  --console <verbose|dotted|quiet|none>  `Console output type`_.
  --dotted                Shortcut for `--console dotted`.
  --quiet                 Shortcut for `--console quiet`.
  -W, --consolewidth <width>  `Sets the width`_ of the console output.
  -C, --consolecolors <auto|on|ansi|off>  `Specifies are colors`_ used on the console.
  -K, --consolemarkers <auto|on|off>  Show `markers on the console`_ when top level
                                      keywords in a test case end.
  --monitorwidth <width>              Deprecated since Robot Framework 2.9.
                                      Use :option:`--consolewidth` instead.
  --monitorcolors <auto|on|ansi|off>  Deprecated since Robot Framework 2.9.
                                      Use :option:`--consolecolors` instead.
  --monitormarkers <auto|on|off>      Deprecated since Robot Framework 2.9.
                                      Use :option:`--consolemarkers` instead.
  -P, --pythonpath <path>  Additional locations to add to the `module search path`_.
  -E, --escape <what:with>   `Escapes characters`_ that are problematic in the console.
  -A, --argumentfile <path>   A text file to `read more arguments`_ from.
  -h, --help              Prints `usage instructions`_.
  --version               Prints the `version information`_.

Command line options for post-processing outputs
------------------------------------------------

  -R, --merge             Changes result combining behavior to `merging <merging outputs_>`__.
  --rerunmerge            Deprecated since Robot Framework 2.8.6.
                          Use :option:`--merge` instead.
  -N, --name <name>       `Sets the name`_ of the top level test suite.
  -D, --doc <document>    `Sets the documentation`_ of the top-level test suite.
  -M, --metadata <name:value>  `Sets free metadata`_ for the top-level test suite.
  -G, --settag <tag>      `Sets the tag(s)`_ to all processed test cases.
  -t, --test <name>       `Selects the test cases by name`_.
  -s, --suite <name>      `Selects the test suites`_ by name.
  -i, --include <tag>     `Selects the test cases`_ by tag.
  -e, --exclude <tag>     `Selects the test cases`_ by tag.
  -c, --critical <tag>    Tests that have the given tag are `considered critical`_.
  -n, --noncritical <tag>  Tests that have the given tag are `not critical`_.
  -d, --outputdir <dir>   Defines where to `create output files`_.
  -o, --output <file>     Sets the path to the generated `output file`_.
  -l, --log <file>        Sets the path to the generated `log file`_.
  -r, --report <file>     Sets the path to the generated `report file`_.
  -x, --xunit <file>      Sets the path to the generated `xUnit compatible result file`_.
  --xunitskipnoncritical  Mark non-critical tests on `xUnit compatible result file`_ as skipped.
  -T, --timestampoutputs  `Adds a timestamp`_ to all output files.
  --splitlog              `Split log file`_ into smaller pieces that open in
                          browser transparently.
  --logtitle <title>      `Sets a title`_ for the generated test log.
  --reporttitle <title>   `Sets a title`_ for the generated test report.
  --reportbackground <colors>  `Sets background colors`_ of the generated report.
  -L, --loglevel <level>  `Sets the threshold level`_ to select log messages.
                          Optionally the default `visible log level`_ can be given
                          separated with a colon (:).
  --suitestatlevel <level>  Defines how many `levels to show`_ in the
                           *Statistics by Suite* table in outputs.
  --tagstatinclude <tag>  `Includes only these tags`_ in the *Statistics by Tag* table.
  --tagstatexclude <tag>  `Excludes these tags`_ from the *Statistics by Tag* table.
  --tagstatcombine <tags:title>  Creates `combined statistics based on tags`_.
  --tagdoc <pattern:doc>  Adds `documentation to the specified tags`_.
  --tagstatlink <pattern:link:title>  Adds `external links`_ to the *Statistics by Tag* table.
  --removekeywords <all|passed|name:pattern|tag:pattern|for|wuks>  `Removes keyword data`_
                          from the generated outputs.
  --flattenkeywords <for|foritem|name:pattern|tag:pattern>  `Flattens keywords`_
                          in the generated outputs.
  --starttime <timestamp>  Sets the `starting time`_ of test execution when creating
                          reports.
  --endtime <timestamp>   Sets the `ending time`_ of test execution when creating reports.
  --nostatusrc            Sets the `return code`_ to zero regardless of failures
                          in test cases. Error codes are returned normally.
  --processemptysuite     Processes output files even if files contain
                          `empty test suites`_.
  --prerebotmodifier <name:args>  Activate `programmatic modification of results`_.
  -C, --consolecolors <auto|on|ansi|off>  `Specifies are colors`_ used on the console.
  --monitorcolors <auto|on|ansi|off>  Deprecated since Robot Framework 2.9.
                                      Use :option:`--consolecolors` instead.
  -P, --pythonpath <path>   Additional locations to add to the `module search path`_.
  -E, --escape <what:with>  `Escapes characters`_ that are problematic in the console.
  -A, --argumentfile <path>   A text file to `read more arguments`_ from.
  -h, --help              Prints `usage instructions`_.
  --version               Prints the `version information`_.


.. _Sets the name: `Setting the name`_
.. _Sets the documentation: `Setting the documentation`_
.. _Sets free metadata: `Setting free metadata`_
.. _Sets the tag(s): `Setting tags`_
.. _Selects the test cases by name: `By test suite and test case names`_
.. _Selects the test suites: `Selects the test cases by name`_
.. _Selects failed tests: `Re-executing failed test cases`_
.. _Selects the test cases: `By tag names`_
.. _considered critical: `Setting criticality`_
.. _not critical: `considered critical`_
.. _ContinueOnFailure: `Continue on failure`_
.. _Skips teardowns: `Handling Teardowns`_
.. _SkipTeardownOnExit: `Handling Teardowns`_
.. _DryRun: `Dry run`_
.. _Randomizes: `Randomizing execution order`_
.. _individual variables: `Setting variables in command line`_

.. _create output files: `Output directory`_
.. _Adds a timestamp: `Timestamping output files`_
.. _Split log file: `Splitting logs`_
.. _Sets a title: `Setting titles`_
.. _Sets background colors: `Setting background colors`_

.. _Sets the threshold level: `Setting log level`_
.. _levels to show: `Configuring displayed suite statistics`_
.. _Includes only these tags: `Including and excluding tag statistics`_
.. _Excludes these tags: `Includes only these tags`_
.. _combined statistics based on tags: `Generating combined tag statistics`_
.. _documentation to the specified tags: `Adding documentation to tags`_
.. _external links: `Creating links from tag names`_

.. _Sets a listener: `Setting listeners`_
.. _an invalid file is skipped: `Warning on invalid files`_
.. _test suites are empty: `When no tests match selection`_
.. _empty test suites: `test suites are empty`_
.. _Sets the width: `Console width`_
.. _Specifies are colors: `Console colors`_
.. _markers on the console: `Console markers`_
.. _Escapes characters: `Escaping complicated characters`_
.. _read more arguments: `Argument files`_
.. _usage instructions: `Getting help and version information`_
.. _version information: `usage instructions`_

.. _Removes keyword data: `Removing and flattening keywords`_
.. _Flattens keywords: `Removes keyword data`_
.. _starting time: `Setting start and end time of execution`_
.. _ending time: `starting time`_
