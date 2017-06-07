*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/should_be_equal.robot
Resource          builtin_resource.robot

*** Test Cases ***
Should Be Equal
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    unicode
    Verify argument type message    ${tc.kws[1].msgs[0]}    float      int
    Verify argument type message    ${tc.kws[2].msgs[0]}    bytes      bytes
    Verify argument type message    ${tc.kws[3].msgs[0]}    unicode    unicode

Should Be Equal case-insensitive
    Check Test Case     ${TESTNAME}

Should Be Equal fails with values
    Check test case    ${TESTNAME}

Should Be Equal fails without values
    Check test case    ${TESTNAME}

Should Be Equal with multiline text uses diff
    [Tags]    no-python26    # diff contains extra spaces on python 2.6
    Check test case    ${TESTNAME}

Should Be Equal with multiline diff text requires both multiline
    Check test case    ${TESTNAME}

Should Be Equal with multiline text will not use diff if values are not included
    Check test case    ${TESTNAME}

Should Be Equal tuple and list with same items fails
    Check test case    ${TESTNAME}

Should Be Equal dictionaries of different type with same items passes
    Check test case    ${TESTNAME}

Should Be Equal with bytes containing non-ascii characters
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    bytes    bytes
    Verify argument type message    ${tc.kws[1].msgs[0]}    bytes    bytes

Should Be Equal with unicode and bytes with non-ascii characters
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    bytes    unicode

Should Be Equal when types differ but string representations are same
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    int

Should Not Be Equal
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    unicode
    Verify argument type message    ${tc.kws[1].msgs[0]}    unicode    int
    Verify argument type message    ${tc.kws[2].msgs[0]}    unicode    unicode

Should Not Be Equal case-insensitive
    Check Test Case     ${TESTNAME}

Should Not Be Equal with bytes containing non-ascii characters
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    bytes    bytes
    Verify argument type message    ${tc.kws[1].msgs[0]}    bytes    unicode
    Verify argument type message    ${tc.kws[2].msgs[0]}    bytes    bytes
