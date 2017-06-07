*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    test_libraries/library_import_failing.robot
Resource        atest_resource.robot

*** Test Cases ***
Invalid Library
    ${path} =  Normalize Path  ${DATADIR}/test_libraries/MyInvalidLibFile.py
    Import Should Have Failed    0    test_libraries/library_import_failing.robot
    ...  Importing test library '${path}' failed: ImportError: I'm not really a library!
    ...  raise ImportError("I'm not really a library!")

Initializing Fails Without Arguments
    Import Should Have Failed    1    test_libraries/library_import_failing.robot
    ...  Initializing test library 'InitializationFailLibrary' with no arguments failed: Initialization failed with arguments 'default 1' and 'default 2'!
    ...  InitializationFailLibrary.py", line 4, in __init__

Initializing Fails With Arguments
    Import Should Have Failed    2    test_libraries/library_import_failing.robot
    ...  Initializing test library 'InitializationFailLibrary' with arguments [ 1 | arg2=2 ] failed: Initialization failed with arguments 1 and 2!
    ...  InitializationFailLibrary.py", line 4, in __init__

Initializing Fails Due To Too Many Arguments
    Import Should Have Failed    3    test_libraries/library_import_failing.robot
    ...  Test Library 'InitializationFailLibrary' expected 0 to 2 arguments, got 3.
    ...  traceback=

Initializing Fails Due To Invalid Named Argument Usage
    Import Should Have Failed    4    test_libraries/library_import_failing.robot
    ...  Test Library 'InitializationFailLibrary' got positional argument after named arguments.
    ...  traceback=

Non-existing Library
    Import Should Have Failed    5    test_libraries/library_import_failing.robot
    ...  Importing test library 'NonExistingLibrary' failed: *Error: *

Non-existing Variable In Library Name
    Import Should Have Failed    6    test_libraries/library_import_failing.robot
    ...  Replacing variables from setting 'Library' failed: Variable '\${non existing nön äscii}' not found.
    ...  traceback=

Non-existing Variable In Library Arguments
    Import Should Have Failed    7    test_libraries/library_import_failing.robot
    ...  Variable '\${nön existing}' not found.
    ...  traceback=

Library Import Without Name
    Import Should Have Failed    8    test_libraries/library_import_failing.robot
    ...  Library setting requires a name
    ...  traceback=

Initializing Java Library Fails
    [Tags]  require-jython
    Import Should Have Failed    9    test_libraries/library_import_failing.robot
    ...  Initializing test library 'InitializationFailJavaLibrary' with no arguments failed: Initialization failed!
    ...  stacktrace=at InitializationFailJavaLibrary.<init>(InitializationFailJavaLibrary.java:4)

Importing library with same name as Python built-in module
    Check Test Case    Name clash with Python builtin-module
