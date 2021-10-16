*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/should_be_equal.robot
Resource          builtin_resource.robot

*** Test Cases ***
Basics
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}
    Verify argument type message    ${tc.kws[1].msgs[0]}
    Verify argument type message    ${tc.kws[2].msgs[0]}    float      int
    Verify argument type message    ${tc.kws[3].msgs[0]}    bytes      bytes
    Verify argument type message    ${tc.kws[4].msgs[0]}

Case-insensitive
    Check Test Case     ${TESTNAME}

Without leading spaces
    Check Test Case     ${TESTNAME}

Without trailing spaces
    Check Test Case     ${TESTNAME}

Without leading and trailing spaces
    Check Test Case     ${TESTNAME}

Do not collapse spaces
    Check Test Case     ${TESTNAME}

Collapse spaces
    Check Test Case     ${TESTNAME}

Fails with values
    Check test case    ${TESTNAME}

Fails without values
    Check test case    ${TESTNAME}

Multiline comparison uses diff
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    foo\nbar\ndar\n\n!=\n\nfoo\nbar\ngar\n\ndar

Multiline comparison with custom message
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    foo\nbar\ndar\n\n!=\n\nfoo\nbar\ngar\n\ndar

Multiline comparison requires both multiline
    Check test case    ${TESTNAME}

Multiline comparison without including values
    Check test case    ${TESTNAME}

formatter=repr
    Check test case    ${TESTNAME}

formatter=repr/ascii with non-ASCII characters
    Check test case    ${TESTNAME}

formatter=repr with multiline
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    foo\nbar\ndar\n\n!=\n\nfoo\nbar\ngar\n\ndar

formatter=repr with multiline and different line endings
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    1\n2\n3\n\n!=\n\n1\n2\n3
    Check Log Message    ${tc.kws[1].msgs[1]}    1\n2\n3\n\n!=\n\n1\n2\n3

formatter=repr/ascii with multiline and non-ASCII characters
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Å\nÄ\n\Ö\n\n!=\n\nÅ\nÄ\n\Ö
    Check Log Message    ${tc.kws[1].msgs[1]}    Å\nÄ\n\Ö\n\n!=\n\nÅ\nÄ\n\Ö

Invalid formatter
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
    Verify argument type message    ${tc.kws[0].msgs[0]}    bytes    str

Types info is added if string representations are same
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    str    int

Should Not Be Equal
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    str    str
    Verify argument type message    ${tc.kws[1].msgs[0]}    str    int
    Verify argument type message    ${tc.kws[2].msgs[0]}    str    str

Should Not Be Equal case-insensitive
    Check Test Case     ${TESTNAME}

Should Not Be Equal without leading spaces
    Check Test Case     ${TESTNAME}

Should Not Be Equal without trailing spaces
    Check Test Case     ${TESTNAME}

Should Not Be Equal without leading and trailing spaces
    Check Test Case     ${TESTNAME}

Should Not Be Equal and do not collapse spaces
    Check Test Case     ${TESTNAME}

Should Not Be Equal and collapse spaces
    Check Test Case     ${TESTNAME}

Should Not Be Equal with bytes containing non-ascii characters
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    bytes    bytes
    Verify argument type message    ${tc.kws[1].msgs[0]}    bytes    str
    Verify argument type message    ${tc.kws[2].msgs[0]}    bytes    bytes
