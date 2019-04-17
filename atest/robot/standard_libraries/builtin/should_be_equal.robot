*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/should_be_equal.robot
Resource          builtin_resource.robot

*** Test Cases ***
Basics
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    unicode
    Verify argument type message    ${tc.kws[1].msgs[0]}    unicode    unicode
    Verify argument type message    ${tc.kws[2].msgs[0]}    float      int
    Verify argument type message    ${tc.kws[3].msgs[0]}    bytes      bytes
    Verify argument type message    ${tc.kws[4].msgs[0]}    unicode    unicode

Case-insensitive
    Check Test Case     ${TESTNAME}

Fails with values
    Check test case    ${TESTNAME}

Fails without values
    Check test case    ${TESTNAME}

Multiline comparison uses diff
    Check test case    ${TESTNAME}

Multiline comparison requires both multiline
    Check test case    ${TESTNAME}

Multiline comparison without including values
    Check test case    ${TESTNAME}

Tuple and list with same items fail
    Check test case    ${TESTNAME}

Dictionaries of different type with same items pass
    Check test case    ${TESTNAME}

Bytes containing non-ascii characters
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    bytes    bytes
    Verify argument type message    ${tc.kws[1].msgs[0]}    bytes    bytes

Unicode and bytes with non-ascii characters
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    bytes    unicode

Types info is added if string representations are same
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
