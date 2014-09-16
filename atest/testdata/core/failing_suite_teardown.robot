*** Setting ***
Suite Setup       Log    Suite setup executed
Suite Teardown    Run Keywords    Fail    first    AND    Fail    second
Default Tags      tag1    tag2

*** Test Case ***
Test 1
    [Documentation]    FAIL Parent suite teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) first
    ...
    ...    2) second
    Log    This is executed normally
    My Keyword

Test 2
    [Documentation]    FAIL Parent suite teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) first
    ...
    ...    2) second
    Log    All tests pass here

*** Keyword ***
My Keyword
    Log    User keywords work normally
    No Operation
