*** Settings ***
Metadata          Initial    Value
Suite Setup       Set Suite Metadata    Setup    Value
Suite Teardown    Set Suite Metadata    Teardown    Another value
Library           Collections

*** Test Cases ***
Set new value
    Set Suite Metadata    New metadata    Set in test
    Metadata variable should have value    New metadata    Set in test

Override existing value
    Set Suite Metadata    Initial    New value
    Metadata variable should have value    Initial    New value

Names are case and space insensitive
    Set Suite Metadata    My Name    overwritten
    Set Suite Metadata    MYname    final value
    Metadata variable should have value    My Name    final value

Append to value
    Set Suite Metadata    To Append    Original    append please
    Metadata variable should have value    To Append    Original
    Set Suite Metadata    toappend    is continued    append please
    Metadata variable should have value    To Append    Original is continued
    Set Suite Metadata    TOAPPEND    \n\ntwice!    append=please
    Metadata variable should have value    To Append    Original is continued \n\ntwice!
    Set Suite Metadata    Version    1.0    append please    separator=,
    Metadata variable should have value    Version    1.0
    Set Suite Metadata    version    2.0    append please    separator=/
    Metadata variable should have value    Version    1.0/2.0
    Set Suite Metadata    ver sion    3.0    append please    separator=/
    Metadata variable should have value    Version    1.0/2.0/3.0

Set top-level suite metadata
    Set Suite Metadata    New metadata    Metadata for    top=yes
    Set Suite Metadata    newmetadata    top level suite    append    top
    Metadata variable should have value    New metadata    Set in test
    Set Suite Metadata    Separator    ${2}    append=yes    top=yes     separator=/
    Set Suite Metadata    Separator    top    append    top    separator=
    Set Suite Metadata    Separator    level    append    top    separator=**

Non-ASCII and non-string names and values
    Set Suite Metadata    ${42}    ${1}
    Metadata variable should have value    42    1
    Set Suite Metadata    42    päivä    append=kyllä
    Metadata variable should have value    42    1 päivä

Modifying \${SUITE METADATA} has no effect also after setting metadata
    [Documentation]    The variable changes but actual metadata does not
    Set Suite Metadata    Cannot be   set otherwise
    Set To Dictionary    ${SUITE METADATA}    Cannot be   really set this way
    Metadata variable should have value    Cannot be   really set this way

*** Keywords ***
Metadata variable should have value
    [Arguments]    ${name}    ${value}
    Should Be Equal    ${SUITE METADATA['${name}']}    ${value}
