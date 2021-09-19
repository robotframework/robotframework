*** Settings ***
Library           Exceptions

*** Test Cases ***
Set Test Message
    [Documentation]    PASS
    ...    *HTML* <b>Hello, world!</b>
    Set Test Message    *HTML* <b>Hello, world!</b>

HTML failure
    [Documentation]    FAIL
    ...    *HTML* <a href='http://robotframework.org'>Robot Framework</a>
    Fail    *HTML* <a href='http://robotframework.org'>Robot Framework</a>

HTML failure with non-generic exception
    [Documentation]    FAIL
    ...    *HTML* ValueError: Invalid <b>value</b>
    ValueError    *HTML* Invalid <b>value</b>

HTML failure in setup
    [Documentation]    FAIL
    ...    *HTML* Setup failed:
    ...    Should be <b>HTML</b>
    [Setup]    Should be true    False    *HTML* Should be <b>HTML</b>
    No operation

HTML failure in teardown
    [Documentation]    FAIL
    ...    *HTML* Teardown failed:
    ...    Should be <b>HTML</b>
    No operation
    [Teardown]    Fail    *HTML*Should be <b>HTML</b>

Normal failure in body and HTML failure in teardown
    [Documentation]    FAIL
    ...    *HTML* Should NOT be &lt;b&gt;HTML&lt;/b&gt;
    ...
    ...    Also teardown failed:
    ...    Should be <b>HTML</b>
    Fail    Should NOT be <b>HTML</b>
    [Teardown]    Fail    *HTML* Should be <b>HTML</b>

HTML failure in body and normal failure teardown
    [Documentation]    FAIL
    ...    *HTML*Should be <b>HTML</b>
    ...
    ...    Also teardown failed:
    ...    Should NOT be &lt;b&gt;HTML&lt;/b&gt;
    Fail    *HTML*Should be <b>HTML</b>
    [Teardown]    Fail    Should NOT be <b>HTML</b>

HTML failure in body and in teardown
    [Documentation]    FAIL
    ...    *HTML* Should be <b>HTML</b>
    ...
    ...    Also teardown failed:
    ...    Should be <b>HTML</b>
    Fail    *HTML* Should be <b>HTML</b>
    [Teardown]    Fail    *HTML*${SPACE*3}Should be <b>HTML</b>

Continuable failures
    [Documentation]    FAIL
    ...    *HTML* Several failures occurred:
    ...
    ...    1) Should be <b>HTML</b>
    ...
    ...    2) Should NOT be &lt;b&gt;HTML&lt;/b&gt;
    ...
    ...    3) Should be <b>HTML</b>
    ...
    ...    4) Should NOT be &lt;b&gt;HTML&lt;/b&gt;
    Run keyword and continue on failure    Fail    *HTML* Should be <b>HTML</b>
    Run keyword and continue on failure    Fail    Should NOT be <b>HTML</b>
    Run keyword and continue on failure    Fail    *HTML* Should be <b>HTML</b>
    Run keyword and continue on failure    Fail    Should NOT be <b>HTML</b>
