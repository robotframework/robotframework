*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/should_be_equal_as_xxx.robot
Resource          builtin_resource.robot

*** Test Cases ***
Should Be Equal As Integers
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}

Should Be Equal As Integers with base
    Check test case    ${TESTNAME}

Should Not Be Equal As Integers
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}

Should Not Be Equal As Integers with base
    Check test case    ${TESTNAME}

Should Be Equal As Numbers
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}

Should Be Equal As Numbers with precision
    Check test case    ${TESTNAME}

Should Not Be Equal As Numbers
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}

Should Not Be Equal As Numbers with precision
    Check test case    ${TESTNAME}

Should Be Equal As Strings
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    int

Should Be Equal As Strings does NFC normalization
    Check test case    ${TESTNAME}

Should Be Equal As Strings case-insensitive
    Check test case    ${TESTNAME}

Should Be Equal As Strings without leading spaces
    Check test case    ${TESTNAME}

Should Be Equal As Strings without trailing spaces
    Check test case    ${TESTNAME}

Should Be Equal As Strings without leading and trailing spaces
    Check test case    ${TESTNAME}

Should Be Equal As Strings and do not collapse spaces
    Check test case    ${TESTNAME}

Should Be Equal As Strings and collapse spaces
    Check test case    ${TESTNAME}

Should Be Equal As Strings repr
    Check test case    ${TESTNAME}

Should Be Equal As Strings multiline
    Check test case    ${TESTNAME}

Should Be Equal As Strings multiline with custom message
    Check test case    ${TESTNAME}

Should Be Equal As Strings repr multiline
    Check test case    ${TESTNAME}

Should Not Be Equal As Strings
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    str    float

Should Not Be Equal As Strings case-insensitive
    Check test case    ${TESTNAME}

Should Not Be Equal As Strings without leading spaces
    Check test case    ${TESTNAME}

Should Not Be Equal As Strings without trailing spaces
    Check test case    ${TESTNAME}

Should Not Be Equal As Strings without leading and trailing spaces
    Check test case    ${TESTNAME}

Should Not Be Equal As Strings and do not collapse spaces
    Check test case    ${TESTNAME}

Should Not Be Equal As Strings and collapse spaces
    Check test case    ${TESTNAME}
