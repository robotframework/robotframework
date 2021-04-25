*** Settings ***
Suite Teardown    Skip    Cannot go on

*** Test Cases ***
Skip In Suite Teardown
    [Documentation]    SKIP
    ...    Skipped in parent suite teardown:
    ...    Cannot go on
    ...
    ...    Earlier message:
    ...    Oh no, a failure
    Fail    Oh no, a failure
