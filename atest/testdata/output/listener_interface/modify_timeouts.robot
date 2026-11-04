*** Test Cases ***
Add test timeout
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    Sleep    1 second

Shorten test timeout
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    1 minute
    Sleep    1 second

Extend test timeout
    [Timeout]    100 milliseconds
    Sleep    200 milliseconds

Remove test timeout
    [Timeout]    100 milliseconds
    Sleep    200 milliseconds

Disable test timeout
    [Timeout]    100 milliseconds
    Sleep    200 milliseconds

Timeout from listener variable
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    Sleep    1 second

Invalid timeout from listener
    [Documentation]    FAIL Setting test timeout failed: Invalid time string 'invalid'.
    No Operation

Timeout in setup
    [Documentation]    FAIL Setup failed:
    ...                Test timeout 100 milliseconds exceeded.
    [Setup]    Sleep    1 second
    No Operation

Unchanged timeout
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    100 milliseconds
    Sleep    1 second

Keyword timeouts can be changed
    [Documentation]    FAIL Keyword timeout 100 milliseconds exceeded.
    Add keyword timeout

Keyword timeouts can be removed
    Remove keyword timeout

*** Keywords ***
Add keyword timeout
    Sleep    1 second

Remove keyword timeout
    [Timeout]    100 milliseconds
    Sleep    200 milliseconds
