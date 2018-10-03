*** Test Cases ***
Timeout in test case level
    [Documentation]    FAIL Emulated timeout inside log_message
    Log    This causes timeout
    Fail    This shouldn't be executed

Timeout inside user keyword
    [Documentation]    FAIL Emulated timeout inside log_message
    Keyword
    Fail    This shouldn't be executed

*** Keywords ***
Keyword
    Log    All log messages cause timeout
