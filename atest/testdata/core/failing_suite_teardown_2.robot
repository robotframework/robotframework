*** Setting ***
Suite Setup       Log    Suite setup executed
Suite Teardown    Fail    Expected failure

*** Variables ***
${ALSO}           \n\nAlso parent suite teardown failed:\nExpected failure

*** Test Case ***
Test Passes
    [Documentation]    FAIL Parent suite teardown failed:\nExpected failure
    Log    This is executed normally
    My Keyword

Test Fails
    [Documentation]    FAIL Failure in test${ALSO}
    Fail    Failure in test

Setup Fails
    [Documentation]    FAIL Setup failed:
    ...    Failure in setup${ALSO}
    [Setup]    Fail    Failure in setup
    No Operation

Teardown Fails
    [Documentation]    FAIL Teardown failed:
    ...    Failure in teardown${ALSO}
    No Operation
    [Teardown]    Fail    Failure in teardown

Test and Teardown Fail
    [Documentation]    FAIL Failure in test
    ...
    ...    Also teardown failed:
    ...    Failure in teardown${ALSO}
    Fail    Failure in test
    [Teardown]    Fail    Failure in teardown

*** Keyword ***
My Keyword
    Log    User keywords work normally
    No Operation
