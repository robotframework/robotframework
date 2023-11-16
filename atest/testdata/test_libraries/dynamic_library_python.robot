*** Settings ***
Library         RunKeywordLibrary
Library         RunKeywordLibrary.RunKeywordButNoGetKeywordNamesLibrary
Library         RunKeywordLibrary.GlobalRunKeywordLibrary
Library         dynamic_libraries/DynamicLibraryWithoutArgspec.py
Library         dynamic_libraries/NonAsciiKeywordNames.py
Library         dynamic_libraries/NonAsciiKeywordNames.py    include_latin1=True
Library         dynamic_libraries/EmbeddedArgs.py
Library         dynamic_libraries/InvalidKeywordNames.py
Library         dynamic_libraries/AsyncDynamicLibrary.py

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

Non-ASCII keyword name works when Unicode
    ${name} =    Unicode nön-äscïï
    Should Be Equal    ${name}    Unicode nön-äscïï
    ${name} =    ☃
    Should Be Equal    ${name}    \u2603
    Should Be Equal    ${name}    ☃

Non-ASCII keyword name works when UTF-8 bytes
    ${name} =    UTF-8 nön-äscïï
    Should Be Equal    ${name}    UTF-8 nön-äscïï

Non-ASCII keyword name fails when other bytes
    [Documentation]  FAIL No keyword with name 'Latin1 nön-äscïï' found.
    Latin1 nön-äscïï

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

Embedded Keyword Arguments
    ${count}  ${item} =  Add 7 Copies Of Coffee To Cart
    Should Be Equal  ${count}-${item}  7-Coffee
    ${count}  ${item} =  add 42 copies of foobar to cart
    Should Be Equal  ${count}-${item}  42-foobar

Dynamic async kw works
    ${result} =    Async Keyword
    Should Be Equal    ${result}    test
