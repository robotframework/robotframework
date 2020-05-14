*** Variables ***
${COUNTER}        ${0}

*** Test Cases ***
Fail until the end
    [Documentation]    FAIL Keyword 'Fail' failed after retrying for 200 milliseconds. The last error was: Not gonna happen
    Wait Until Keyword Succeeds    0.2    0.05    Fail    Not gonna happen

Passes before timeout
    Wait Until Keyword Succeeds    2    0.01    Fail Two Times

Warnings
    Wait Until Keyword Succeeds    2    0.01    Warn And Fail Two Times

One Warning
    [Documentation]    FAIL Keyword 'Warn On First And Fail Two Times' failed after retrying for 500 milliseconds. The last error was: Until the end
    Wait Until Keyword Succeeds    0.5    0.01    Warn On First And Fail Two Times

Nested
    [Documentation]    FAIL Keyword 'Nested Wait' failed after retrying for 500 milliseconds. The last error was: Keyword 'Fail' failed after retrying for 50 milliseconds. The last error was: Always
    Wait Until Keyword Succeeds    0.5    0.01    Nested Wait

*** Keywords ***
Fail Two Times
    Set Test Variable    $COUNTER    ${COUNTER + 1}
    Run Keyword If    ${COUNTER} != ${3}    FAIL    not enough tries

Warn And Fail Two Times
    Log    DANGER MR. ROBINSON!!    WARN
    Fail Two Times

Warn On First And Fail Two Times
    Run Keyword If    ${COUNTER} == ${0}    log    danger zone    WARN
    Set Test Variable    $COUNTER    ${COUNTER + 1}
    Fail    Until the end

Nested Wait
    Wait Until Keyword Succeeds    0.05    0.01    Fail    Always

