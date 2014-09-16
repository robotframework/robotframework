*** Settings ***
Library         UnicodeLibrary

*** Test Cases ***
Unicode In Log Messages
    Print Unicode Strings
    Log    Français

Unicode Return Value
    ${msg} =    Evaluate    u'Fran\\xe7ais'
    Should Be Equal    ${msg}    Français
    Log    ${msg}

Unicode In Return Value Attributes
    ${obj} =  Print And Return Unicode Object
    Log  ${obj.message}

Unicode Failure
    Raise Unicode Error

Unicode Failure In Setup
    [Setup]  Raise Unicode Error
    No Operation

Unicode Failure In Teardown
    No Operation
    [Teardown]  Raise Unicode Error

Unicode Failure In Teardown After Normal Failure
    Fail  Just ASCII here
    [Teardown]  Raise Unicode Error

Ünïcödë Tëst änd Këywörd Nämës
    Ünïcödë Këywörd Nämë

*** Keywords ***
Ünïcödë Këywörd Nämë
    Log    Hyvää päivää
