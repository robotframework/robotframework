*** Setting ***
Suite Setup       Non-Existing Keyword
Suite Teardown    My TD

*** Test Case ***
Test 1
    [Documentation]    FAIL Parent suite setup failed:
    ...    No keyword with name 'Non-Existing Keyword' found.
    Fail    This is not executed

Test 2
    [Documentation]    FAIL Parent suite setup failed:
    ...    No keyword with name 'Non-Existing Keyword' found.
    Fail    This is not executed

*** Keyword ***
My TD
    Log    Hello from suite teardown!
    No Operation
