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
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    foo\nbar\ndar\n\n!=\n\nfoo\nbar\ngar\n\ndar

Multiline comparison requires both multiline
    Check test case    ${TESTNAME}

Multiline comparison without including values
    Check test case    ${TESTNAME}

formatter=repr
    Check test case    ${TESTNAME}

formatter=repr/ascii with non-ASCII characters on Python 2
    [Tags]    require-py2
    Check test case    ${TESTNAME}

formatter=repr/ascii with non-ASCII characters on Python 3
    [Tags]    require-py3
    Check test case    ${TESTNAME}

formatter=repr with multiline
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    foo\nbar\ndar\n\n!=\n\nfoo\nbar\ngar\n\ndar

formatter=repr with multiline and different line endings
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    1\n2\n3\n\n!=\n\n1\n2\n3
    Check Log Message    ${tc.kws[1].msgs[1]}    1\n2\n3\n\n!=\n\n1\n2\n3

formatter=repr/ascii with multiline and non-ASCII characters on Python 2
    [Tags]    require-py2
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Å\nÄ\n\Ö\n\n!=\n\nÅ\nÄ\n\Ö
    Check Log Message    ${tc.kws[1].msgs[1]}    Å\nÄ\n\Ö\n\n!=\n\nÅ\nÄ\n\Ö

formatter=repr/ascii with multiline and non-ASCII characters on Python 3
    [Tags]    require-py3
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
