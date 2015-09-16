*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/library_import_failing.robot
Resource        atest_resource.robot

*** Test Cases ***
Invalid Library
    ${path} =  Normalize Path  ${DATADIR}/test_libraries/MyInvalidLibFile.py
    Import Should Have Failed  0
    ...  Importing test library '${path}' failed: ImportError: I'm not really a library!
    ...  raise ImportError("I'm not really a library!")

Initializing Fails Without Arguments
    Import Should Have Failed  1
    ...  Initializing test library 'InitializationFailLibrary' with no arguments failed: Initialization failed with arguments 'default 1' and 'default 2'!
    ...  InitializationFailLibrary.py", line 4, in __init__

Initializing Fails With Arguments
    Import Should Have Failed  2
    ...  Initializing test library 'InitializationFailLibrary' with arguments [ 1 | arg2=2 ] failed: Initialization failed with arguments 1 and 2!
    ...  InitializationFailLibrary.py", line 4, in __init__

Initializing Fails Due To Too Many Arguments
    Import Should Have Failed  3
    ...  Test Library 'InitializationFailLibrary' expected 0 to 2 arguments, got 3.

Initializing Fails Due To Invalid Named Argument Usage
    Import Should Have Failed  4
    ...  Test Library 'InitializationFailLibrary' got positional argument after named arguments.

Non-existing Library
    Import Should Have Failed  5
    ...  Importing test library 'NonExistingLibrary' failed: ImportError:

Non-existing Variable In Library Name
    Import Should Have Failed  6
    ...  Replacing variables from setting 'Library' failed: Variable '\${non existing nön äscii}' not found.

Non-existing Variable In Library Arguments
    Import Should Have Failed  7
    ...  Variable '\${nön existing}' not found.

Library Import Without Name
    Import Should Have Failed  8
    ...  Library setting requires a name

Initializing Java Library Fails
    [Tags]  require-jython
    Import Should Have Failed  9
    ...  Initializing test library 'InitializationFailJavaLibrary' with no arguments failed: Initialization failed!
    ...  at InitializationFailJavaLibrary.<init>(InitializationFailJavaLibrary.java:4)

*** Keywords ***
Import Should Have Failed
    [Arguments]  ${index}  ${expected message}  ${expected traceback}=
    ${message} =  Set Variable  ${ERRORS.msgs[${index}].message}
    ${path} =   Normalize Path  ${DATADIR}/test_libraries/library_import_failing.robot
    Should Start With  ${message}  Error in file '${path}': ${expected message}
    Should Contain  ${message}  ${expected traceback}
