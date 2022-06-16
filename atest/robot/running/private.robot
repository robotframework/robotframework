*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/private.robot
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

Keyword With Same Name Should Resolve Public Keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message
    ...    ${tc.body[0].body[0]}
    ...    There were both public and private keyword found with the name 'Same Name', 'private.Same Name' being public and 'private2.Same Name' being private. The public keyword is used. To select explicitly, and to get rid of this warning, use either 'private.Same Name' or 'private2.Same Name'.
    ...    WARN
    Length Should Be    ${tc.body[0].body}    2

If Both Keywords Are Private Raise Multiple Keywords Found
    Check Test Case    ${TESTNAME}

*** Keywords ***
Private Call Warning Should Be
    [Arguments]    ${name}    @{messages}
    FOR    ${message}    IN    @{messages}
        Check Log Message     ${message}
        ...    Keyword '${name}' is private and should only be called by keywords in the same file.
        ...    WARN
    END
