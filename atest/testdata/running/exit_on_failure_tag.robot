*** Settings ***
Test Tags        robot:exit-on-failure

*** Test Cases ***
Passing test with the tag has not special effect
    Log    Nothing to worry here!

Failing test without the tag has no special effect
    [Documentation]    FAIL    Something bad happened!
    [Tags]    -robot:exit-on-failure
    Fail    Something bad happened!

Failing test with the tag initiates exit-on-failure
    [Documentation]    FAIL    Something worse happened!
    Fail    Something worse happened!

Subsequent tests are not run 1
    [Documentation]    FAIL    Test execution stopped due to a fatal error.
    Fail    Not executed.

Subsequent tests are not run 2
    [Documentation]    FAIL    Test execution stopped due to a fatal error.
    Fail    Not executed.
