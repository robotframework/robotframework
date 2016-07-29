*** Variable ***
${EXPECTED FAILURE}    Expected failure
${TEARDOWN MESSAGE}    Teardown message

*** Keywords ***

Keyword that Fails with Teardown
    Fail    ${EXPECTED FAILURE}
    [Teardown]    Run Keyword If Keyword Failed    Log    Hello from keyword teardown!

Keyword that Does Not Fail with Teardown
    No Operation
    [Teardown]    Run Keyword If Keyword Failed    Fail    ${NOT EXECUTED}

*** Test Case ***
Run Keyword If keyword Failed When Keyword Fails
    [Documentation]    FAIL Expected failure
    Keyword that Fails with Teardown

Run Keyword If Keyword Failed When Keyword Does Not Fail
    Keyword that Does Not Fail with Teardown
