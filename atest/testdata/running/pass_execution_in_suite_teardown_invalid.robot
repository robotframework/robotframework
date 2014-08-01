*** Settings ***
Force Tags        force1    force2
Suite Teardown    Pass Execution   message    tag     setting    fails

*** Test Cases ***
Test in suite with invalid Pass Execution usage in Suite Teardown
    [Documentation]    FAIL
    ...    Test is run normally.
    ...
    ...    Also parent suite teardown failed:
    ...    'Set Tags' cannot be used in suite teardown.
    Fail    Test is run normally.
