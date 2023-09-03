*** Settings ***
Library           GetKeywordNamesLibrary
Library           dynamic_libraries/InvalidKeywordNames.py    hybrid=True

*** Test Cases ***
Passing, Logging And Returning
    ${ret} =    Get Keyword That Passes    Hello    world
    Should Be Equal    ${ret}    Hello, world

Failing
    [Documentation]    FAIL    Failure: Hi tellus
    Get Keyword That Fails    Hi tellus

Keyword Implemented In Library Class Itself
    ${ret} =    Keyword In Library Itself
    Should Be Equal    ${ret}    No need for __getattr__ here!!

Non Existing Attribute
    [Documentation]    FAIL    No keyword with name 'Non-existing attribute' found.
    Non-existing attribute

Named Keyword Is Not Method
    [Documentation]    FAIL    No keyword with name 'not_method_or_function' found.
    not_method_or_function

Unexpected error getting attribute
    [Documentation]    FAIL    No keyword with name 'Unexpected error getting attribute' found.
    Unexpected error getting attribute

Name Set Using 'robot_name' Attribute
    Name Set Using 'robot_name' Attribute

Old Name Doesn't Work If Name Set Using 'robot_name'
    [Documentation]    FAIL    No keyword with name 'Name Set In Method Signature' found.
    Name Set In Method Signature

'robot_name' Attribute Set To None
    Keyword Name Should Not Change

Embedded Keyword Arguments
    ${count}    ${item} =    Add 7 Copies Of Coffee To Cart
    Should Be Equal    ${count}-${item}    7-Coffee

Name starting with an underscore is OK
    Starting with underscore is OK

__init__ exposed as keyword
    Init
