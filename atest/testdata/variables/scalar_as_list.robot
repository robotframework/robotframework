*** Settings ***
Library         Collections
Variables       scalar_lists.py

*** Test Cases ***
Scalar List As List Variable
    Test Scalar As List    @{LIST}

Scalar Iterable As List Variable
    Test Scalar As List    @{ITERABLE}

Scalar Variable As List With Extended Syntax
    Test Scalar As List    @{EXTENDED.list}
    Test Scalar As List    @{EXTENDED['whatever']}
    ${hyvää} =    Set Variable    spam,eggs
    ${list} =    Evaluate    [[21]]
    Test Scalar As List    @{hyvää.split(',')}    @{list[0]}

Extended syntax with non-list value
    [Documentation]    FAIL Value of variable '\@{EXTENDED.string}' is not list or list-like.
    Log Many    @{EXTENDED.string}

Non-alphanumeric characters in name
    ${"spëciäl" ch@rs?!} =    Copy List    ${LIST}
    Test Scalar As List    @{"spëciäl" ch@rs?!}

String Cannot Be Used As List Variable
    [Documentation]    FAIL Value of variable '\@{TEST NAME}' is not list or list-like.
    Log Many    @{TEST NAME}

Non-Iterables Cannot Be Used As List Variable
    [Documentation]    FAIL Value of variable '\@{INTEGER}' is not list or list-like.
    ${integer} =    Set Variable    ${42}
    Log Many    @{INTEGER}

*** Keywords ***
Test Scalar As List
    [Arguments]    ${a1}    ${a2}    ${a3}
    Should Be Equal    ${a1}    spam
    Should Be Equal    ${a2}    eggs
    Should Be Equal    ${a3}    ${21}
