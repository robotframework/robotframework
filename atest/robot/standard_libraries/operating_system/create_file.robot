*** Settings ***
Suite Setup       Run Tests
...    -v SYSTEM_ENCODING:${SYSTEM_ENCODING} -v CONSOLE_ENCODING:${CONSOLE_ENCODING}
...    standard_libraries/operating_system/create_file.robot
Resource          atest_resource.robot

*** Keywords ***
Check for Secret Value Not in Log Messages
    [Arguments]    ${tc}    ${value}
    FOR    ${kw}    IN    @{tc.body}
        FOR   ${i}    ${msg}    IN ENUMERATE    @{kw.messages}
            Should Not Contain     ${value}     ${msg.message}
            ...    msg=Keyword "${kw.name}" logged the secret (log index ${i})
            ...    values=${FALSE}
        END
    END

*** Test Cases ***
Create File With Default Content
    Check Test Case    ${TESTNAME}

Create File With Content
    Check Test Case    ${TESTNAME}

Create Multiline File
    Check Test Case    ${TESTNAME}

Create Non-ASCII File With Default Encoding
    Check Test Case    ${TESTNAME}

Create File With Encoding
    Check Test Case    ${TESTNAME}

Create File With System Encoding
    Check Test Case    ${TESTNAME}

Create File With Console Encoding
    Check Test Case    ${TESTNAME}

Create File With Non-ASCII Name
    Check Test Case    ${TESTNAME}

Create File With Space In Name
    Check Test Case    ${TESTNAME}

Create File To Non-Existing Directory
    Check Test Case    ${TESTNAME}

Create File with Secret as Content
    ${tc}=    Check Test Case    ${TESTNAME}
    Check for Secret Value Not in Log Messages    ${tc}    should-not-be-logged-1234567abcd

Creating File Fails If Encoding Is Incorrect
    Check Test Case    ${TESTNAME}

Create Binary File Using Bytes
    Check Test Case    ${TESTNAME}

Create Binary File Using Unicode
    Check Test Case    ${TESTNAME}

Creating Binary File Using Unicode With Ordinal > 255 Fails
    Check Test Case    ${TESTNAME}

Append To File
    Check Test Case    ${TESTNAME}

Append To File with Secret as Content
    ${tc}=    Check Test Case    ${TESTNAME}
    Check for Secret Value Not in Log Messages    ${tc}    should-not-be-logged-1234567abcd

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
