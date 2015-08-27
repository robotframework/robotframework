Robot Framework 2.9
===================

Robot Framework 2.9 is a new release with **UPDATE** enhancements and bug
fixes. It was released on Thursday August 27, 2015.

Questions and comments related to the release can be sent to the
`robotframework-users <http://groups.google.com/group/robotframework-users>`_
and possible bugs submitted to the
`issue tracker <https://github.com/robotframework/robotframework/issues>`__.

If you have `pip <http://pip-installer.org>`_ installed, just run
``pip install --update robotframework``. Otherwise see `installation
instructions <../../INSTALL.rst>`_.

Most important enhancements
---------------------------

**EXPLAIN** or remove these.

- #532 Variables should not leak to lower level keywords (alpha 3)
- #1450 Dictionary variable type (alpha 1)
- #1561 Support Python style `**kwargs` with user keywords using `&{kwargs}` syntax (alpha 1)
- #1905 Store list and scalar variables in same namespace (alpha 1)
- #925 Keyword categorization (i.e. tagging) support (alpha 2)
- #1270 Run Keyword If Test (Failed / Passed) does not detect failure in teardown (alpha 3)
- #1737 Standard libraries should not be importable in Python w/o `robot.libraries` prefix (alpha 1)
- #1931 Timeouts can cause sporadic failures with IronPython (alpha 1)
- #2004 `--ExitOnFailure` does not work if test/suite setup/teardown fails (alpha 2)
- #2018 DateTime: DST problems when calculating with dates (alpha 3)
- #1805 Contribution instructions (rc 1)
- #1818 Embedded arguments in keywords defined in test libraries (alpha 1)
- #1840 Libdoc: Show keywords by tags (alpha 2)
- #1928 Drop Python/Jython 2.5 support to ease adding support for Python 3 (alpha 1)
- #1943 Use lighter and more neutral colors for report and log html page (beta 1)
- #1952 `FOR ... IN ZIP ...` and `FOR ... IN ENUMERATE` (beta 2)
- #1965 Support yaml files as first class variable file (alpha 2)
- #1976 Support programmatic modifications of test data and results as part of normal execution (alpha 2)
- #1991 Include Jython 2.7 in standalone jar (alpha 2)
- #2040 Add variables to evaluation namespace of `Evaluate`, `Run Keyword If`, ... (beta 2)
- #293 BuiltIn: New `Reload Library` keyword (alpha 2)
- #317 Less verbose and quiet console outputs (alpha 3)

Backwards incompatible changes
------------------------------

**EXPLAIN** or remove these.

- #532 Variables should not leak to lower level keywords (alpha 3)
- #1905 Store list and scalar variables in same namespace (alpha 1)
- #1270 Run Keyword If Test (Failed / Passed) does not detect failure in teardown (alpha 3)
- #1737 Standard libraries should not be importable in Python w/o `robot.libraries` prefix (alpha 1)
- #2018 DateTime: DST problems when calculating with dates (alpha 3)
- #1928 Drop Python/Jython 2.5 support to ease adding support for Python 3 (alpha 1)
- #1611 Variable assignment should not be part of keyword name with `--removekeywords`, in logs, in listener interface, or in other APIs (alpha 2)
- #1440 Remove attribute ROBOT_EXIT_FOR_LOOP deprecated in 2.8 (alpha 1)
- #1603 Support `**kwargs` with `BuiltIn.Call Method` keywords (alpha 1)
- #1865 Support disabling command line options accepting no values using `no` prefix (e.g. `--dryrun` -> `--nodryrun`) (alpha 1)
- #1910 Require exact number of keyword return value when assigning multiple scalar variables (alpha 1)
- #1913 Move `Create Dictionary` to BuiltIn and enhance to preserve order, allow accessing keys as attributes, etc. (alpha 1)
- #1962 Disallow using keyword with embedded arguments as normal keywords (alpha 1)
- #1983 PYTHONPATH environment variable should not be processed with Jython or IronPython (alpha 2)
- #2020 Do not write empty elements or attributes to output.xml (alpha 3)
- #1815 Keyword name conflict involving Remote keyword should cause failure, not warning (alpha 1)
- #2016 `FAIL` should not be useable as a normal log level (alpha 3)
- #2019 Execution directory should not be added to module search path (`PYTHONPATH`) (alpha 2)
- #1775 Remove deprecated syntax for repeating single keyword (alpha 1)
- #1919 Remove possibility to setting scalar variables with lists value using `Set Test/Suite/Global Variable` keyword (alpha 1)
- #1923 Remove deprecated `--runmode` option (alpha 1)
- #1924 Remove unused internal functions, classes, etc. (alpha 1)
- #1925 Remove deprecated `--xunitfile` option (alpha 1)
- #2031 Console colors and markers: Fail if given value is invalid and remove outdated `FORCE` color value (alpha 3)
- #2039 OperatingSystem and Dialogs: Remove partial support for running without Robot Framework itself (beta 1)

Deprecated features
-------------------

**EXPLAIN** or remove these.

- #1773 Deprecate `OperatingSystem.Start Process` keyword (alpha 1)
- #1774 Officially deprecate `DeprecatedBuiltIn` and `DeprecatedOperatingSystem` (alpha 1)
- #1841 Deprecate old listener API (alpha 1)
- #2027 Deprecate `--monitorxxx` options in favor of `--consolexxx` (alpha 3)
- #2063 Deprecate using same setting multiple times (rc 1)
- #1642 Deprecate `--runfailed` and `--rerunmerge` options (alpha 1)
- #1918 Deprecate old `Meta: Name` syntax for specifying test suite metadata (alpha 1)

Acknowledgements
----------------

**UPDATE** based on AUTHORS.txt.

Full list of fixes and enhancements
-----------------------------------

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - #532
      - bug
      - critical
      - Variables should not leak to lower level keywords
    * - #1450
      - enhancement
      - critical
      - Dictionary variable type
    * - #1561
      - enhancement
      - critical
      - Support Python style `**kwargs` with user keywords using `&{kwargs}` syntax
    * - #1905
      - enhancement
      - critical
      - Store list and scalar variables in same namespace
    * - #925
      - enhancement
      - critical
      - Keyword categorization (i.e. tagging) support
    * - #1270
      - bug
      - high
      - Run Keyword If Test (Failed / Passed) does not detect failure in teardown
    * - #1737
      - bug
      - high
      - Standard libraries should not be importable in Python w/o `robot.libraries` prefix
    * - #1931
      - bug
      - high
      - Timeouts can cause sporadic failures with IronPython
    * - #2004
      - bug
      - high
      - `--ExitOnFailure` does not work if test/suite setup/teardown fails
    * - #2018
      - bug
      - high
      - DateTime: DST problems when calculating with dates
    * - #1805
      - enhancement
      - high
      - Contribution instructions
    * - #1818
      - enhancement
      - high
      - Embedded arguments in keywords defined in test libraries
    * - #1840
      - enhancement
      - high
      - Libdoc: Show keywords by tags
    * - #1928
      - enhancement
      - high
      - Drop Python/Jython 2.5 support to ease adding support for Python 3
    * - #1943
      - enhancement
      - high
      - Use lighter and more neutral colors for report and log html page
    * - #1952
      - enhancement
      - high
      - `FOR ... IN ZIP ...` and `FOR ... IN ENUMERATE`
    * - #1965
      - enhancement
      - high
      - Support yaml files as first class variable file
    * - #1976
      - enhancement
      - high
      - Support programmatic modifications of test data and results as part of normal execution
    * - #1991
      - enhancement
      - high
      - Include Jython 2.7 in standalone jar
    * - #2040
      - enhancement
      - high
      - Add variables to evaluation namespace of `Evaluate`, `Run Keyword If`, ...
    * - #293
      - enhancement
      - high
      - BuiltIn: New `Reload Library` keyword
    * - #317
      - enhancement
      - high
      - Less verbose and quiet console outputs
    * - #1611
      - bug
      - medium
      - Variable assignment should not be part of keyword name with `--removekeywords`, in logs, in listener interface, or in other APIs
    * - #1900
      - bug
      - medium
      - Log messages lost if library `__init__` imports or initializes other libraries
    * - #1908
      - bug
      - medium
      - Telnet option negotiation loop
    * - #1992
      - bug
      - medium
      - Listeners are not unregistered when using `TestSuite.run` API
    * - #2062
      - bug
      - medium
      - Not possible to print to stdout/stderr by listeners or otherwise inside `Run Keyword` variants
    * - #1440
      - enhancement
      - medium
      - Remove attribute ROBOT_EXIT_FOR_LOOP deprecated in 2.8
    * - #1603
      - enhancement
      - medium
      - Support `**kwargs` with `BuiltIn.Call Method` keywords
    * - #1728
      - enhancement
      - medium
      - Support setting child suite variables with `Set Suite Variable`
    * - #1743
      - enhancement
      - medium
      - Make keyword prefix (library name) less visible than keywords in HTML reports
    * - #1773
      - enhancement
      - medium
      - Deprecate `OperatingSystem.Start Process` keyword
    * - #1774
      - enhancement
      - medium
      - Officially deprecate `DeprecatedBuiltIn` and `DeprecatedOperatingSystem`
    * - #1826
      - enhancement
      - medium
      - Process: Better support on Jython 2.7 (termination, signals, pid)
    * - #1834
      - enhancement
      - medium
      - String: Support partial match with `Get Lines Matching RegExp`
    * - #1835
      - enhancement
      - medium
      - Allow giving a custom name to keywords implemented using the static and the hybrid APIs
    * - #1841
      - enhancement
      - medium
      - Deprecate old listener API
    * - #1865
      - enhancement
      - medium
      - Support disabling command line options accepting no values using `no` prefix (e.g. `--dryrun` -> `--nodryrun`)
    * - #1869
      - enhancement
      - medium
      - Variable errors should not exit `Wait Until Keyword Succeeds`, `Run Keyword And Expect Error`, etc.
    * - #1910
      - enhancement
      - medium
      - Require exact number of keyword return value when assigning multiple scalar variables
    * - #1911
      - enhancement
      - medium
      - Accept list variable as a wildcard anywhere when assigning variables
    * - #1913
      - enhancement
      - medium
      - Move `Create Dictionary` to BuiltIn and enhance to preserve order, allow accessing keys as attributes, etc.
    * - #1914
      - enhancement
      - medium
      - Catenate cell values when creating scalar variable in variable table
    * - #1916
      - enhancement
      - medium
      - Expose `ERROR` log level to custom libraries
    * - #1927
      - enhancement
      - medium
      - Remote: Support accessing keys of returned dicts using attribute access
    * - #1935
      - enhancement
      - medium
      - Support keyword tags with `--flattenkeywords` and `--removekeywords`
    * - #1958
      - enhancement
      - medium
      - `Log Many`: Support logging `&{dictionary}` variable items
    * - #1959
      - enhancement
      - medium
      - `Wait Until Keyword Succeeds`: Support giving wait time as number of times to retry
    * - #1962
      - enhancement
      - medium
      - Disallow using keyword with embedded arguments as normal keywords
    * - #1969
      - enhancement
      - medium
      - Allow giving listener and model modifier instances to `robot.run` and `TestSuite.run`
    * - #1970
      - enhancement
      - medium
      - Enhance ROBOT_LIBRARY_LISTENER to accept a list of listeners
    * - #1972
      - enhancement
      - medium
      - User Guide: Switch examples to use plain text format instead of HTML format
    * - #1983
      - enhancement
      - medium
      - PYTHONPATH environment variable should not be processed with Jython or IronPython
    * - #1985
      - enhancement
      - medium
      - String: New `Get Regexp Matches` keyword
    * - #1990
      - enhancement
      - medium
      - Avoid Python 3 incompatible type checks
    * - #1998
      - enhancement
      - medium
      - Pass keyword and library names separately to listeners
    * - #2020
      - enhancement
      - medium
      - Do not write empty elements or attributes to output.xml
    * - #2027
      - enhancement
      - medium
      - Deprecate `--monitorxxx` options in favor of `--consolexxx`
    * - #2028
      - enhancement
      - medium
      - Tag patterns starting with `NOT`
    * - #2029
      - enhancement
      - medium
      - When exiting gracefully, skipped tests should get automatic `robot-exit` tag
    * - #2030
      - enhancement
      - medium
      - Notify listeners about library, resource and variable file imports
    * - #2032
      - enhancement
      - medium
      - Document that test and keyword tags with `robot-` prefix are reserved
    * - #2036
      - enhancement
      - medium
      - `BuiltIn.Get Variables`: Support getting variables without `${}` decoration
    * - #2038
      - enhancement
      - medium
      - Consistent usage of Boolean arguments in standard libraries
    * - #2063
      - enhancement
      - medium
      - Deprecate using same setting multiple times
    * - #1815
      - bug
      - low
      - Keyword name conflict involving Remote keyword should cause failure, not warning
    * - #1906
      - bug
      - low
      - Free keyword arguments (`**kwargs`) names cannot contain equal signs or trailing backslashes
    * - #1922
      - bug
      - low
      - Screenshot library causes deprecation warning with wxPython 3.x
    * - #1997
      - bug
      - low
      - User Guide has outdated links to test templates
    * - #2002
      - bug
      - low
      - Keyword and test names with urls or quotes create invalid html on log and report
    * - #2003
      - bug
      - low
      - Checking is stdout/stderr stream terminal causes exception if stream's buffer is detached
    * - #2016
      - bug
      - low
      - `FAIL` should not be useable as a normal log level
    * - #2019
      - bug
      - low
      - Execution directory should not be added to module search path (`PYTHONPATH`)
    * - #2043
      - bug
      - low
      - BuiltIn: Some `Should` keyword only consider Python `True` true and other values false
    * - #1642
      - enhancement
      - low
      - Deprecate `--runfailed` and `--rerunmerge` options
    * - #1775
      - enhancement
      - low
      - Remove deprecated syntax for repeating single keyword
    * - #1897
      - enhancement
      - low
      - Clean-up reference to RF 2.6 and older from User Guide and other documentation
    * - #1898
      - enhancement
      - low
      - Improve error message for "Else" instead of "ELSE"
    * - #1918
      - enhancement
      - low
      - Deprecate old `Meta: Name` syntax for specifying test suite metadata
    * - #1919
      - enhancement
      - low
      - Remove possibility to setting scalar variables with lists value using `Set Test/Suite/Global Variable` keyword
    * - #1921
      - enhancement
      - low
      - More flexible syntax to deprecate keywords
    * - #1923
      - enhancement
      - low
      - Remove deprecated `--runmode` option
    * - #1924
      - enhancement
      - low
      - Remove unused internal functions, classes, etc.
    * - #1925
      - enhancement
      - low
      - Remove deprecated `--xunitfile` option
    * - #1929
      - enhancement
      - low
      - OperatingSystem: Enhance documentation about path separators
    * - #1945
      - enhancement
      - low
      - Enhance documentation of `Run Keyword If` return values
    * - #2021
      - enhancement
      - low
      - Update XSD schemas 
    * - #2022
      - enhancement
      - low
      - Document that preformatted text with spaces in Robot data requires escaping
    * - #2031
      - enhancement
      - low
      - Console colors and markers: Fail if given value is invalid and remove outdated `FORCE` color value
    * - #2033
      - enhancement
      - low
      - Use `setuptools` for installation when available
    * - #2037
      - enhancement
      - low
      - `BuiltIn.Evaluate`: Support any mapping as a custom namespace
    * - #2039
      - enhancement
      - low
      - OperatingSystem and Dialogs: Remove partial support for running without Robot Framework itself
    * - #2041
      - enhancement
      - low
      - Collections: New keyword `Convert To Dictionary`
    * - #2045
      - enhancement
      - low
      - BuiltIn: Log argument types in DEBUG level not INFO

Altogether 94 issues. View on `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3A2.9>`__.
