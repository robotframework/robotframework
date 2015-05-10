*** Settings ***
Library         GetKeywordNamesLibrary

*** Test Cases ***
Passing, Logging And Returning
    ${ret} =  Get Keyword That Passes  Hello  world
    Should Be Equal  ${ret}  Hello, world

Failing
    [Documentation]  FAIL Failure: Hi tellus
    Get Keyword That Fails  Hi tellus

Keyword Implemented In Library Class Itself
    ${ret} =  Keyword In Library Itself
    Should Be Equal  ${ret}  No need for __getattr__ here!!

Non Existing Keyword
    [Documentation]  FAIL No keyword with name 'Non Existing Keyword' found.
    Non Existing Keyword

Named Keyword Is Not Method
    [Documentation]  FAIL No keyword with name 'This is not keyword' found.
    This is not keyword

Name Set Using 'robot_name' Attribute
    Name Set Using Robot Name Attribute

Old Name Doesn't Work If Name Set Using 'robot_name'
    [Documentation]  FAIL No keyword with name 'Name Set In Method Signature' found.
    Name Set In Method Signature

'robot_name' Attribute Set To None
    Keyword Name Should Not Change

Embedded Keyword Arguments
    ${count}  ${item} =  Add 7 Copies Of Coffee To Cart
    Should Be Equal  ${count}-${item}  7-Coffee
