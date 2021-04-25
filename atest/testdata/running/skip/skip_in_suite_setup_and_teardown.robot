*** Settings ***
Suite Setup       Skip    Skip me!
Suite Teardown    Skip    Skip me too!

*** Test Cases ***
Skip In Suite Setup And Teardown
    [Documentation]    SKIP
    ...    Skipped in parent suite teardown:
    ...    Skip me too!
    ...
    ...    Earlier message:
    ...    Skipped in parent suite setup:
    ...    Skip me!
    Fail    Should not be executed.
