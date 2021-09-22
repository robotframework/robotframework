*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    test_libraries/library_import_failing.robot
Resource        atest_resource.robot

*** Test Cases ***
Invalid Library
    ${path} =    Normalize Path    ${DATADIR}/test_libraries/MyInvalidLibFile.py
    Error in file    0    test_libraries/library_import_failing.robot    2
    ...    Importing library '${path}' failed:
    ...    ImportError: I'm not really a library!
    ...    traceback=raise ImportError("I'm not really a library!")

Initializing Fails Without Arguments
    Error in file    1    test_libraries/library_import_failing.robot    3
    ...    Initializing library 'InitializationFailLibrary' with no arguments failed:
    ...    Initialization failed with arguments 'default 1' and 'default 2'!
    ...    traceback=InitializationFailLibrary.py", line 4, in __init__

Initializing Fails With Arguments
    Error in file    2    test_libraries/library_import_failing.robot    4
    ...    Initializing library 'InitializationFailLibrary' with arguments [[] 1 | arg2=2 ] failed:
    ...    Initialization failed with arguments 1 and 2!
    ...    traceback=InitializationFailLibrary.py", line 4, in __init__

Initializing Fails Due To Too Many Arguments
    Error in file    3    test_libraries/library_import_failing.robot    5
    ...    Library 'InitializationFailLibrary' expected 0 to 2 arguments, got 3.

Initializing Fails Due To Invalid Named Argument Usage
    Error in file    4    test_libraries/library_import_failing.robot    6
    ...    Library 'InitializationFailLibrary' got positional argument after named arguments.

Non-existing Library
    Error in file    5    test_libraries/library_import_failing.robot    7
    ...    Importing library 'NonExistingLibrary' failed: *Error: *
    ...    traceback=None

Non-existing Variable In Library Name
    Error in file    6    test_libraries/library_import_failing.robot    8
    ...    Replacing variables from setting 'Library' failed:
    ...    Variable '\${non existing nön äscii}' not found.

Non-existing Variable In Library Arguments
    Error in file    7    test_libraries/library_import_failing.robot    9
    ...    Variable '\${nön existing}' not found.

Library Import Without Name
    Error in file    8    test_libraries/library_import_failing.robot    10
    ...    Library setting requires value.

Importing library with same name as Python built-in module
    Check Test Case    Name clash with Python builtin-module
