*** Test Cases ***
Short Sleep
    Sleep    100ms

Long Sleep
    [Documentation]    FAIL Total Execution timeout 1 second exceeded.
    Sleep    2s

Very Long Sleep
    [Documentation]    FAIL Total Execution timeout 1 second exceeded.
    Sleep    5s
