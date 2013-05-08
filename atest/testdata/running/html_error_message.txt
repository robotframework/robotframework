*** Test Cases ***
HTML Failure
    [Documentation]    FAIL *HTML* <a href='http://robotframework.org'>Robot Framework</a>
    Fail    *HTML* <a href='http://robotframework.org'>Robot Framework</a>

Set Test Message
    [Documentation]    PASS *HTML* <b>Hello, world!</b>
    Set Test Message    *HTML* <b>Hello, world!</b>
