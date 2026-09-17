*** Settings ***
Library           Collections

*** Test Cases ***
Set new value
    Set Test Metadata    New metadata    Set in test
    Metadata variable should have value    New metadata    Set in test

Override existing value
    [Metadata]    Initial    Value
    Set Test Metadata    Initial    New value
    Metadata variable should have value    Initial    New value

Names are case and space insensitive
    Set Test Metadata    My Name    overwritten
    Set Test Metadata    MYname    final value
    Metadata variable should have value    My Name    final value

Append to value
    Set Test Metadata    To Append    Original    append please
    Metadata variable should have value    To Append    Original
    Set Test Metadata    toappend    is continued    append please
    Metadata variable should have value    To Append    Original is continued
    Set Test Metadata    TOAPPEND    \n\ntwice!    append=please
    Metadata variable should have value    To Append    Original is continued \n\ntwice!
    Set Test Metadata    Version    1.0    append please    separator=,
    Metadata variable should have value    Version    1.0
    Set Test Metadata    version    2.0    append please    separator=/
    Metadata variable should have value    Version    1.0/2.0
    Set Test Metadata    ver sion    3.0    append please    separator=/
    Metadata variable should have value    Version    1.0/2.0/3.0

Non-ASCII and non-string names and values
    Set Test Metadata    ${42}    ${1}
    Metadata variable should have value    42    1
    Set Test Metadata    42    päivä    append=kyllä
    Metadata variable should have value    42    1 päivä

Modifying \${TEST METADATA} has no effect also after setting metadata
    [Documentation]    The variable changes but actual metadata does not
    Set Test Metadata    Cannot be    set otherwise
    Set To Dictionary    ${TEST METADATA}    Cannot be    really set this way
    Metadata variable should have value    Cannot be    really set this way

Set Task Metadata as alias for Set Test Metadata
    Set Task Metadata    Task    Value
    Metadata variable should have value    Task    Value
    Set Task Metadata    task    is continued    append=yes
    Metadata variable should have value    Task    Value is continued

Set in test setup
    [Setup]    Set Test Metadata    Setup    Value
    Metadata variable should have value    Setup    Value

Set in test teardown
    No Operation
    [Teardown]    Set Test Metadata    Teardown    Another value

Metadata is test specific
    Should Be Empty    ${TEST METADATA}

*** Keywords ***
Metadata variable should have value
    [Arguments]    ${name}    ${value}
    Should Be Equal    ${TEST METADATA['${name}']}    ${value}
