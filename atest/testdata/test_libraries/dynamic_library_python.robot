*** Settings ***
Library         RunKeywordLibrary
Library         RunKeywordLibrary.RunKeywordButNoGetKeywordNamesLibrary
Library         RunKeywordLibrary.GlobalRunKeywordLibrary
Library         ${CURDIR}/dynamic_libraries/DynamicLibraryWithoutArgspec.py


*** Test Cases ***
Passing, Logging and Returning
    ${ret} =  RunKeywordLibrary. Run Keyword That Passes  Hi  tellus
    Should Be Equal  ${ret}  Hi, tellus

Failing
    [Documentation]  FAIL Failure: Hello world
    RunKeywordLibrary. Run Keyword That Fails  Hello world

Global Dynamic Library
    [Documentation]  FAIL Failure
    ${ret} =  RunKeywordLibrary. GlobalRunKeywordLibrary. RunKeyword That Passes  Hi  tellus  and  Hello  Mars!
    Should Be Equal  ${ret}  Hi, tellus, and, Hello, Mars!
    RunKeywordLibrary. GlobalRunKeywordLibrary. RunKeyword That Fails

Run Keyword in Static Library
    [Documentation]  PASS
    Run Keyword
    Some Other Keyword
    ${ret} =  Run Keyword  return  this
    Should Be Equal  ${ret}  return this
    ${ret} =  Some Other Keyword  this is  returned
    Should Be Equal  ${ret}  this is returned

Not Found Keyword
    [Documentation]  FAIL No keyword with name 'Get Keyword That Does Not Exist' found.
    Get Keyword That Does Not Exist

Dynamic libraries should work without argument specification
    [Documentation]    PASS
    Do Something    print this
    Do Something else    something    something else
    Do Something else    something
    Do Something else    something    y=12

Dynamic libraries should match named arguments same way as with user keywords
    [Documentation]    As these named arguments do not match the keyword's
    ...                argument spec, it should use them as strings to match the
    ...                positional arguments.
    ...                e.g. this should print strings 'x', 'y=1' and 'z=2'
    Do something third    x    y=1    z=2


