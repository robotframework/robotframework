*** Settings ***
Library         NonAsciiLibrary

*** Test Cases ***
Non-ASCII Log Messages
    Print NonASCII Strings
    Log    Français
    Sleep    0.001

Non-ASCII Return Value
    ${msg} =    Evaluate    u'Fran\\xe7ais'
    Should Be Equal    ${msg}    Français
    Log    ${msg}

Non-ASCII In Return Value Attributes
    ${obj} =  Print And Return NonASCII Object
    Log  ${obj.message}

Non-ASCII Failure
    [Tags]    täg
    Raise NonASCII Error

Non-ASCII Failure In Setup
    [Setup]  Raise NonASCII Error
    No Operation

Non-ASCII Failure In Teardown
    No Operation
    [Teardown]  Raise NonASCII Error

Non-ASCII Failure In Teardown After Normal Failure
    Fail  Just ASCII here
    [Teardown]  Raise NonASCII Error

Ñöñ-ÄŚÇÏÏ Tëśt äņd Këywörd Nämës, Спасибо
    Ñöñ-ÄŚÇÏÏ Këywörd Nämë

*** Keywords ***
Ñöñ-ÄŚÇÏÏ Këywörd Nämë
    Log    Hyvää päivää
