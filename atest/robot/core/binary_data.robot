*** Settings ***
Documentation     Tests for libraries writes binary data into STDOUT and raising exceptions containing it.
Suite Setup       My Run Tests
Resource          atest_resource.robot
Variables         ../../resources/unicode_vars.py

*** Test Cases ***
Print Bytes
    [Documentation]    Check that bytes 0-255, incl. control chars, can be printed ok.
    ...    The actual result depends on the interpreter and operating system.
    ${tc} =    Check Test Case    ${TESTNAME}
    # First check some printable bytes and control chars.
    # Control chars should result to an empty string.
    FOR    ${index}    ${exp}    IN
    ...    0      ${EMPTY}
    ...    1      ${EMPTY}
    ...    7      ${EMPTY}
    ...    8      ${EMPTY}
    ...    9      \t
    ...    10     \n
    ...    32     ${SPACE}
    ...    39     '
    ...    92     \\
    ...    82     R
    ...    111    o
    ...    98     b
    ...    111    o
    ...    116    t
    ...    123    {
    ...    127    \x7f
        Check Log Message    ${tc.kws[0].msgs[${index}]}    Byte ${index}: '${exp}'
    END
    # Check that all bytes were really written without errors.
    FOR    ${index}    IN RANGE    256
        Should Start With    ${tc.kws[0].msgs[${index}].message}    Byte ${index}:
    END
    Check Log Message    ${tc.kws[0].msgs[-1]}    All bytes printed successfully

Byte Error
    [Documentation]    Check an exception containing control chars is handled ok
    Check Test Case    ${TESTNAME}

Byte Error In Setup And Teardown
    Check Test Case    ${TESTNAME}

Binary Data
    [Documentation]    Make sure even totally binary data doesn't break anything
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Binary data printed successfully

*** Keywords ***
My Run Tests
    Run Tests    ${EMPTY}    core/binary_data.robot
    ${stderr} =    Get Stderr
    Should Be Empty    ${stderr}
