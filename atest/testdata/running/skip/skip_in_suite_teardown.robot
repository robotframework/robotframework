*** Settings ***
Suite Teardown    Skip    Cannot go on

*** Test Cases ***
Skip In Suite Teardown
    [Documentation]    SKIP Skipped in parent suite teardown:\nCannot go on\n\nEarlier message:\nOh no, a failure
    Fail    Oh no, a failure
