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
    ${warning}=    Catenate
    ...    Both public and private keywords with name 'Same Name' found.
    ...    The public keyword 'private.Same Name' is used and
    ...    private keyword 'private2.Same Name' ignored.
    ...    To select explicitly, and to get rid of this warning, use the long name of the keyword.
    Public And Private Keyword Conflict Warning Should Be    ${warning}    ${tc.body[0].body[0]}    ${ERRORS[3]}
    Length Should Be    ${tc.body[0].body}    2

If Both Keywords Are Private Raise Multiple Keywords Found
    Check Test Case    ${TESTNAME}

If One Keyword Is Public And Multiple Private Keywords Run Public And Warn
    ${tc}=    Check Test Case    ${TESTNAME}
    ${warning}=    Catenate
    ...    Both public and private keywords with name 'Possible Keyword' found.
    ...    The public keyword 'private.Possible Keyword' is used and
    ...    private keywords 'private2.Possible Keyword' and 'private3.Possible Keyword' ignored.
    ...    To select explicitly, and to get rid of this warning, use the long name of the keyword.
    Public And Private Keyword Conflict Warning Should Be    ${warning}    ${tc.body[0].body[0].body[0]}    ${ERRORS[4]}
    Length Should Be    ${tc.body[0].body[0].body}    2

*** Keywords ***
Private Call Warning Should Be
    [Arguments]    ${name}    @{messages}
    FOR    ${message}    IN    @{messages}
        Check Log Message     ${message}
        ...    Keyword '${name}' is private and should only be called by keywords in the same file.
        ...    WARN
    END

Public And Private Keyword Conflict Warning Should Be
    [Arguments]    ${warning}    @{messages}
    FOR    ${message}    IN    @{messages}
        Check Log Message    ${message}    ${warning}    WARN
    END
