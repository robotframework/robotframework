```robotframework
*** Variables ***
${msg}    Expected failure

*** Test Cases ***
Suite2 Test
    [Documentation]    FAIL    Expected failure
    Fail    ${msg}
```