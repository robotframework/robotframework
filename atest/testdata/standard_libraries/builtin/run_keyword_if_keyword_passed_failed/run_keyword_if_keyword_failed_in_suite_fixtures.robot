*** Setting ***
Suite Setup       Run Keyword If Keyword Failed    Fail    ${NON EXISTING}
Suite Teardown    Run Keyword If Keyword Failed    Fail    ${NON EXISTING}

*** Test Case ***
Run Keyword If keyword Failed Can't Be Used In Suite Setup or Teardown
    [Documentation]    FAIL Parent suite setup failed:
    ...    Keyword 'Run Keyword If Keyword Failed' can only be used in keyword teardown.
    ...
    ...    Also parent suite teardown failed:
    ...    Keyword 'Run Keyword If Keyword Failed' can only be used in keyword teardown.
    No Operation
