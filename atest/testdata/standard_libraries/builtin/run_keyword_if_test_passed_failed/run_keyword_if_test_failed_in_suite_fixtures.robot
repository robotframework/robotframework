*** Settings ***
Suite Setup       Run Keyword If Test Failed    Fail    ${NON EXISTING}
Suite Teardown    Run Keyword If Test Failed    Fail    ${NON EXISTING}

*** Test Cases ***
Run Keyword If test Failed Can't Be Used In Suite Setup or Teardown
    [Documentation]    FAIL Parent suite setup failed:
    ...    Keyword 'Run Keyword If Test Failed' can only be used in test teardown.
    ...
    ...    Also parent suite teardown failed:
    ...    Keyword 'Run Keyword If Test Failed' can only be used in test teardown.
    No Operation
