*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/run.robot
Resource          atest_resource.robot

*** Keywords ***
Check for Secret Value Not in Log Messages
    [Arguments]    ${tc}    ${value}
    FOR    ${kw}    IN    @{tc.body}
        FOR   ${i}    ${msg}    IN ENUMERATE    @{kw.messages}
            Should Not Contain     ${value}     ${msg.message}
            ...    msg=Keyword "${kw.name}" logged the secret (log index ${i})
            ...    values=False
        END
    END

*** Test Cases ***
Run
    Check Test Case    ${TESTNAME}

Run With RC And Stdout Checks
    Check Test Case    ${TESTNAME}

Run With RC Checks
    Check Test Case    ${TESTNAME}

Run With Stdout Checks
    Check Test Case    ${TESTNAME}

Run With Stderr
    Check Test Case    ${TESTNAME}

Run With Stderr Redirected To Stdout
    Check Test Case    ${TESTNAME}

Run With Stderr Redirected To File
    Check Test Case    ${TESTNAME}

Run When Command Writes Lot Of Stdout And Stderr
    Check Test Case    ${TESTNAME}

Run And Return RC
    Check Test Case    ${TESTNAME}

Run And Return RC And Output
    Check Test Case    ${TESTNAME}

Run Non-ascii Command Returning Non-ascii Output
    Check Test Case    ${TESTNAME}

Trailing Newline Is Removed Automatically
    Check Test Case    ${TESTNAME}

It Is Possible To Start Background Processes
    Check Test Case    ${TESTNAME}

Run With Secret Command
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1,1]}    Running command '<redacted>'.
    Check for Secret Value Not in Log Messages    ${tc}    should-not-be-logged-1234567abcd

Run And Return RC With Secret Command
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1,1]}    Running command '<redacted>'.
    Check for Secret Value Not in Log Messages    ${tc}    should-not-be-logged-1234567abcd

Run And Return RC And Output With Secret Command
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1,1]}    Running command '<redacted>'.
    Check for Secret Value Not in Log Messages    ${tc}    should-not-be-logged-1234567abcd