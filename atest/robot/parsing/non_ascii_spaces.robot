*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    parsing/non_ascii_spaces.robot
Resource         atest_resource.robot

*** Test Cases ***
In suite settings
    ${tc} =    Check Test Case    In test and keywords
    Check Log Message    ${tc.setup[0, 0]}       ':\\xa0:'
    Check Log Message    ${tc.setup[1, 0]}       : :
    Check Log Message    ${tc.teardown[0, 0]}    ':\\u1680:'
    Check Log Message    ${tc.teardown[1, 0]}    : :

In test and keywords
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0]}      ':\\xa0:'
    Check Log Message    ${tc[0, 1, 0]}      : :
    Check Log Message    ${tc[1, 0, 0]}      ':\\u1680:'
    Check Log Message    ${tc[1, 1, 0]}      : :
    Check Log Message    ${tc[2, 0, 0]}      ':\\u3000:'
    Check Log Message    ${tc[2, 1, 0]}      :　:

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
    Check Log Message    ${tc[0, 3, 0, 0]}    Should be executed

In inline ELSE IF
    Check Test Case    ${TESTNAME}

With embedded arguments and BDD prefixes
    Check Test Case    ${TESTNAME}
