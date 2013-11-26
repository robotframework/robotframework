*** Settings ***
Library         RunKeywordLibraryJava
Library         RunKeywordButNoGetKeywordNamesLibraryJava
Library         DynamicJavaLibraryWithLists


*** Test Cases ***
Run Keyword
    [Documentation]  FAIL Failure: Hello world
    Run Keyword That Passes
    ${ret} =  Run Keyword That Passes  Hi  tellus
    Should Be Equal  ${ret}  Hitellus
    Run Keyword That Fails  Hello world

Run Keyword But No Get Keyword Names
    [Documentation]  PASS
    Run Keyword  name
    ${ret} =  Run Keyword  return  this
    Should Be Equal  ${ret}  return this
    ${ret} =  Some Other Keyword  this is  returned
    Should Be Equal  ${ret}  this is returned

Not Found Keyword
    [Documentation]  FAIL No keyword with name 'Get Keyword That Does Not Exist' found.
    Get Keyword That Does Not Exist

Can use lists instead of arrays in dynamic API
    ${ret} =    Keyword using lists
    Should Be Equal    ${ret}    ${EMPTY}
    ${ret} =    Keyword using lists    hello
    Should Be Equal    ${ret}    hello
    ${ret} =    Keyword using lists    hello    ${42}
    Should Be Equal    ${ret}    hello 42
    ${ret} =    Keyword using lists    second=hello
    Should Be Equal    ${ret}    foo hello
