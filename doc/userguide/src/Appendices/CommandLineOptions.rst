Command line options
====================

This appendix lists all the command line options that are available
when `executing test cases`_  and when `post-processing outputs`_.
Also environment variables affecting execution and post-processing
are listed.

.. contents::
   :depth: 2
   :local:

Command line options for test execution
---------------------------------------

  --rpa                   Turn on `generic automation`_ mode.
  --language <lang>       Activate localization_. `lang` can be a name or a code
                          of a `built-in language <Translations_>`__, or a path
                          or a module name of a custom language file.
  -F, --extension <value>  `Parse only these files`_ when executing a directory.
  -I, --parseinclude <pattern>  `Parse only matching files`_ when executing a directory.
  -N, --name <name>       `Sets the name`_ of the top-level test suite.
  -D, --doc <document>    `Sets the documentation`_ of the top-level test suite.
  -M, --metadata <name:value>  `Sets free metadata`_ for the top level test suite.
  -G, --settag <tag>      `Sets the tag(s)`_ to all executed test cases.
  -t, --test <name>       `Selects the test cases by name`_.
  --task <name>           Alias for :option:`--test` that can be used when `executing tasks`_.
  -s, --suite <name>      `Selects the test suites`_ by name.
  -R, --rerunfailed <file>  `Selects failed tests`_ from an earlier `output file`_
                          to be re-executed.
  -S, --rerunfailedsuites <file>  `Selects failed test suites`_ from an earlier
                          `output file`_ to be re-executed.
  -i, --include <tag>     `Selects the test cases`_ by tag.
  -e, --exclude <tag>     `Selects the test cases`_ by tag.
  --skip <tag>            Tests having given tag will be `skipped`_. Tag can be a pattern.
  --skiponfailure <tag>   Tests having given tag will be `skipped`_ if they fail.
  -v, --variable <name:value>   Sets `individual variables`_.
  -V, --variablefile <path:args>  Sets variables using `variable files`_.
  -d, --outputdir <dir>   Defines where to `create output files`_.
  -o, --output <file>     Sets the path to the generated `output file`_.
  --legacyoutput          Creates output file in `Robot Framework 6.x compatible format`_.
  -l, --log <file>        Sets the path to the generated `log file`_.
  -r, --report <file>     Sets the path to the generated `report file`_.
  -x, --xunit <file>      Sets the path to the generated `xUnit compatible result file`_.
  -b, --debugfile <file>  A `debug file`_ that is written during execution.
  -T, --timestampoutputs  `Adds a timestamp`_ to `output files`_ listed above.
  --splitlog              `Split log file`_ into smaller pieces that open in
                          browser transparently.
  --logtitle <title>      `Sets a title`_ for the generated test log.
  --reporttitle <title>   `Sets a title`_ for the generated test report.
  --reportbackground <colors>  `Sets background colors`_ of the generated report.
  --maxerrorlines <lines>  Sets the number of `error lines`_ shown in report when tests fail.
  --maxassignlength <characters>  Sets the number of characters shown in log when
                           `variables are assigned <Automatically logging assigned variable value_>`__.
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
  --expandkeywords <name:pattern|tag:pattern>  Automatically `expand keywords`_
                          in the generated log file.
  --removekeywords <all|passed|name:pattern|tag:pattern|for|while|wuks>  `Removes keyword data`_
                          from the generated log file.
  --flattenkeywords <for|while|iteration|name:pattern|tag:pattern>  `Flattens keywords`_
                          in the generated log file.
  --listener <name:args>  `Sets a listener`_ for monitoring test execution.
  --nostatusrc            Sets the `return code`_ to zero regardless of failures
                          in test cases. Error codes are returned normally.
  --runemptysuite         Executes tests also if the selected `test suites are empty`_.
  --dryrun                In the `dry run`_ mode tests are run without executing
                          keywords originating from test libraries. Useful for
                          validating test data syntax.
  -X, --exitonfailure     `Stops test execution <Stopping when first test case fails_>`__
                          if any test fails.
  --exitonerror           `Stops test execution <Stopping on parsing or execution error_>`__
                          if any error occurs when parsing test data, importing libraries, and so on.
  --skipteardownonexit    `Skips teardowns`_ if test execution is prematurely stopped.
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
  -P, --pythonpath <path>  Additional locations to add to the `module search path`_.
  -A, --argumentfile <path>   A text file to `read more arguments`_ from.
  -h, --help              Prints `usage instructions`_.
  --version               Prints the `version information`_.

Command line options for post-processing outputs
------------------------------------------------

  --rpa                   Turn on `generic automation`_ mode.
  -R, --merge             Changes result combining behavior to `merging <merging outputs_>`__.
  -N, --name <name>       `Sets the name`_ of the top level test suite.
  -D, --doc <document>    `Sets the documentation`_ of the top-level test suite.
  -M, --metadata <name:value>  `Sets free metadata`_ for the top-level test suite.
  -G, --settag <tag>      `Sets the tag(s)`_ to all processed test cases.
  -t, --test <name>       `Selects the test cases by name`_.
  --task <name>           Alias for :option:`--test`.
  -s, --suite <name>      `Selects the test suites`_ by name.
  -i, --include <tag>     `Selects the test cases`_ by tag.
  -e, --exclude <tag>     `Selects the test cases`_ by tag.
  -d, --outputdir <dir>   Defines where to `create output files`_.
  -o, --output <file>     Sets the path to the generated `output file`_.
  --legacyoutput          Creates output file in `Robot Framework 6.x compatible format`_.
  -l, --log <file>        Sets the path to the generated `log file`_.
  -r, --report <file>     Sets the path to the generated `report file`_.
  -x, --xunit <file>      Sets the path to the generated `xUnit compatible result file`_.
  -T, --timestampoutputs  `Adds a timestamp`_ to `output files`_ listed above.
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
  --expandkeywords <name:pattern|tag:pattern>  Automatically `expand keywords`_
                          in the generated log file.
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
  -P, --pythonpath <path>   Additional locations to add to the `module search path`_.
  -A, --argumentfile <path>   A text file to `read more arguments`_ from.
  -h, --help              Prints `usage instructions`_.
  --version               Prints the `version information`_.

.. _generic automation: `Task execution`_
.. _Parse only these files: `Selecting files to parse`_
.. _Parse only matching files: `Selecting files to parse`_
.. _Sets the name: `Setting suite name`_
.. _Sets the documentation: `Setting suite documentation`_
.. _Sets free metadata: `Setting free suite metadata`_
.. _Sets the tag(s): `Setting test tags`_
.. _Selects the test cases by name: `By test names`_
.. _Selects the test suites: `By suite names`_
.. _Selects failed test suites: `Re-executing failed test suites`_
.. _Selects failed tests: `Re-executing failed test cases`_
.. _Selects the test cases: `By tag names`_
.. _ContinueOnFailure: `Continue on failure`_
.. _Skips teardowns: `Handling Teardowns`_
.. _SkipTeardownOnExit: `Handling Teardowns`_
.. _DryRun: `Dry run`_
.. _Randomizes: `Randomizing execution order`_
.. _individual variables: `Setting variables in command line`_

.. _create output files: `Output directory`_
.. _Robot Framework 6.x compatible format: `Legacy output file format`_
.. _Adds a timestamp: `Timestamping output files`_
.. _Split log file: `Splitting logs`_
.. _Sets a title: `Setting titles`_
.. _Sets background colors: `Setting background colors`_
.. _error lines: `Limiting error message length in reports`_

.. _Sets the threshold level: `Setting log level`_
.. _levels to show: `Configuring displayed suite statistics`_
.. _Includes only these tags: `Including and excluding tag statistics`_
.. _Excludes these tags: `Includes only these tags`_
.. _combined statistics based on tags: `Generating combined tag statistics`_
.. _documentation to the specified tags: `Adding documentation to tags`_
.. _external links: `Creating links from tag names`_

.. _Sets a listener: `Setting listeners`_
.. _test suites are empty: `When no tests match selection`_
.. _empty test suites: `test suites are empty`_
.. _Sets the width: `Console width`_
.. _Specifies are colors: `Console colors`_
.. _markers on the console: `Console markers`_
.. _read more arguments: `Argument files`_
.. _usage instructions: `Getting help and version information`_
.. _version information: `usage instructions`_

.. _expand keywords: `Automatically expanding keywords`_
.. _Removes keyword data: `Removing and flattening keywords`_
.. _Flattens keywords: `Removes keyword data`_
.. _starting time: `Setting start and end time of execution`_
.. _ending time: `starting time`_


Environment variables for execution and post-processing
-------------------------------------------------------

``ROBOT_OPTIONS`` and ``REBOT_OPTIONS``
    Space separated list of default options to be placed
    `in front of any explicit options`__ on the command line.

``ROBOT_SYSLOG_FILE``
    Path to a syslog_ file where Robot Framework writes internal
    information about parsing test case files and running
    tests.

``ROBOT_SYSLOG_LEVEL``
    Log level to use when writing to the syslog_ file.

``ROBOT_INTERNAL_TRACES``
    When set to any non-empty value, Robot Framework's
    internal methods are included in `error tracebacks`__.

__ `ROBOT_OPTIONS and REBOT_OPTIONS environment variables`_
__ `Debugging problems`_
