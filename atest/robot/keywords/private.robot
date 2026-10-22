*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/private.robot
Resource          atest_resource.robot

*** Test Cases ***
Suite can call local private keyword
    Length Should Be    ${SUITE.setup.body}    1

Suite calling private resource keyword causes warning
    Private Call Warning Should Be    private.Private Keyword In Resource
    ...    ${SUITE.teardown[0]}    ${ERRORS[4]}
    Length Should Be    ${SUITE.teardown.body}    2

Test can call local public keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc[0].body}    1

Test can call local private keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc[0].body}    1

Test can call public resource keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc[0].body}    1

Test calling private resource keyword causes warning
    ${tc}=    Check Test Case    ${TESTNAME}
    Private Call Warning Should Be    private.Private Keyword In Resource
    ...    ${tc[0, 0]}    ${ERRORS[0]}
    Length Should Be    ${tc[0].body}    2

Resource keyword calling private keyword in another resource causes warning
    ${tc}=    Check Test Case    ${TESTNAME}
    Private Call Warning Should Be    private2.Private Keyword In Resource 2
    ...    ${tc[0, 0, 0]}    ${ERRORS[1]}
    Length Should Be    ${tc[0, 0].body}    2

Resource keyword calling private keyword in suite file causes warning
    ${tc}=    Check Test Case    ${TESTNAME}
    Private Call Warning Should Be    Private Keyword In Suite File
    ...    ${tc[0, 0, 0]}    ${ERRORS[2]}
    Length Should Be    ${tc[0, 0].body}    2

Local private keyword in resource has precedence over keywords in another resource
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0, 0]}    private.resource
    Check Log Message    ${tc[0, 1, 0, 0]}    private.resource

Search order has precedence over local private keyword in resource
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0, 0]}    private2.resource

Imported public keyword has precedence over imported private keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0]}       private2.resource
    Check Log Message    ${tc[1, 0, 0, 0]}    private2.resource

Raise multiple keywords error if all keywords are private
    Check Test Case    ${TESTNAME}

Raise multiple keywords error if more than one keyword is public
    Check Test Case    ${TESTNAME}

Test can call local private keyword with embedded arguments
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc[0].body}    1

Resource keyword calling private keyword with embedded arguments in suite file causes warning
    ${tc}=    Check Test Case    ${TESTNAME}
    Private Call Warning Should Be    Private Keyword With \${argument}
    ...    ${tc[0, 0, 0]}    ${ERRORS[3]}
    Length Should Be    ${tc[0, 0].body}    2

*** Keywords ***
Private Call Warning Should Be
    [Arguments]    ${name}    @{messages}
    FOR    ${message}    IN    @{messages}
        Check Log Message     ${message}
        ...    Keyword '${name}' is private and should only be called by keywords in the same file.
        ...    WARN
    END
