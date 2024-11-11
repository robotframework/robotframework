*** Test Cases ***
Skip With Pass
    [Documentation]    PASS
    [Template]    Run Keyword
    Skip    Skipped
    Log    Passed

Skip With Fail
    [Documentation]    FAIL Failed
    [Template]    Run Keyword
    Log    Passed
    Skip    Skipped
    Log    Passed
    Skip    Skipped
    Fail    Failed

All Skips
    [Documentation]    SKIP All iterations skipped.
    [Template]    Run Keyword
    Skip    Skipped
    Skip    Skipped
