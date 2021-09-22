*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    parsing/non_ascii_spaces.robot
Resource         atest_resource.robot

*** Test Cases ***
In suite settings
    ${tc} =    Check Test Case    In test and keywords
    Check Log Message    ${tc.setup.kws[0].msgs[0]}       ':\\xa0:'
    Check Log Message    ${tc.setup.kws[1].msgs[0]}       : :
    Check Log Message    ${tc.teardown.kws[0].msgs[0]}    ':\\u1680:'
    Check Log Message    ${tc.teardown.kws[1].msgs[0]}    : :

In test and keywords
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}      ':\\xa0:'
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}      : :
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}      ':\\u1680:'
    Check Log Message    ${tc.kws[1].kws[1].msgs[0]}      : :
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}      ':\\u3000:'
    Check Log Message    ${tc.kws[2].kws[1].msgs[0]}      :　:

As separator
    Check Test Case    ${TESTNAME}

With pipes
    Check Test Case    ${TESTNAME}

In header
    Check Test Case    ${TESTNAME}

In test casename
    Check Test Case    ${TESTNAME}

In WITH NAME
    Check Test Case    ${TESTNAME}

In FOR separator
    Check Test Case    ${TESTNAME}

In ELSE IF
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.body[0].body[3].body[0].msgs[0]}    Should be executed
