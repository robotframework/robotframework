*** Variables ***
${COUNTER}        ${0}

*** Test Cases ***
Fail until the end
    [Documentation]    FAIL Keyword 'Fail' failed after retrying for 50 milliseconds. The last error was: Not gonna happen
    Wait Until Keyword Succeeds    0.05    0.01    Fail    Not gonna happen

Passes before timeout
    Wait Until Keyword Succeeds    2    0.01    Fail Two Times

Warnings
    Wait Until Keyword Succeeds    2    0.01    Warn And Fail Two Times

One Warning
    [Documentation]    FAIL Keyword 'Warn Once And Fail Afterwards' failed after retrying for 42 milliseconds. The last error was: Until the end
    Wait Until Keyword Succeeds    0.042    0.01    Warn Once And Fail Afterwards

Nested
    [Documentation]    FAIL Keyword 'Nested Wait' failed after retrying for 123 milliseconds. The last error was: Keyword 'Fail' failed after retrying for 50 milliseconds. The last error was: Always
    Wait Until Keyword Succeeds    0.123    0.01    Nested Wait

*** Keywords ***
Fail Two Times
    Set Test Variable    $COUNTER    ${COUNTER + 1}
    IF    ${COUNTER} < 3    Fail    Not enough attempts

Warn And Fail Two Times
    Log    DANGER MR. ROBINSON!!    WARN
    Fail Two Times

Warn Once And Fail Afterwards
    IF    ${COUNTER} == 0    Log    Danger zone    WARN
    Set Test Variable    $COUNTER    ${COUNTER + 1}
    Fail    Until the end

Nested Wait
    Wait Until Keyword Succeeds    0.05    0.01    Fail    Always

