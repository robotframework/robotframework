*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/private.robot
Resource          atest_resource.robot

*** Test Cases ***
Valid Usage With Local Keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.body[0].body}    1

Invalid Usage With Local Keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Private Call Warning Should Be    Private Keyword    ${tc.body[0].body[0]}    ${ERRORS[0]}
    Length Should Be    ${tc.body[0].body}    2

Valid Usage With Resource Keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.body[0].body}    1

Invalid Usage With Resource Keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Private Call Warning Should Be    private.Private Keyword In Resource    ${tc.body[0].body[0]}    ${ERRORS[1]}
    Length Should Be    ${tc.body[0].body}    2

Invalid Usage in Resource File
    ${tc}=    Check Test Case    ${TESTNAME}
    Private Call Warning Should Be    private2.Private Keyword In Resource 2   ${tc.body[0].body[0].body[0]}    ${ERRORS[2]}
    Length Should Be    ${tc.body[0].body[0].body}    2

Local Private Keyword In Resource File Has Precedence Over Keywords In Another Resource
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.body[0].body[0].body[0].msgs[0]}    private.resource
    Check Log Message    ${tc.body[0].body[1].body[0].msgs[0]}    private.resource

Search Order Has Precedence Over Local Private Keyword In Resource File
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.body[0].body[0].body[0].msgs[0]}    private2.resource

Imported Public Keyword Has Precedence Over Imported Private Keywords
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.body[0].body[0].msgs[0]}            private2.resource
    Check Log Message    ${tc.body[1].body[0].body[0].msgs[0]}    private2.resource

If All Keywords Are Private Raise Multiple Keywords Found
    Check Test Case    ${TESTNAME}

If More Than Two Keywords Are Public Raise Multiple Keywords Found
    Check Test Case    ${TESTNAME}

*** Keywords ***
Private Call Warning Should Be
    [Arguments]    ${name}    @{messages}
    FOR    ${message}    IN    @{messages}
        Check Log Message     ${message}
        ...    Keyword '${name}' is private and should only be called by keywords in the same file.
        ...    WARN
    END
