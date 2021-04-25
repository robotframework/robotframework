*** Settings ***
Suite Setup       Fail    Fail me!
Suite Teardown    Skip    Skip me!

*** Test Cases ***
Skip In Suite Teardown After Fail In Setup
    [Documentation]    SKIP
    ...    Skipped in parent suite teardown:
    ...    Skip me!
    ...
    ...    Earlier message:
    ...    Parent suite setup failed:
    ...    Fail me!
    Fail    Should not be executed.
