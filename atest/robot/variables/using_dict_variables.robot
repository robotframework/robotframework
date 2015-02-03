*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/using_dict_variables.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
From variable table
    Check Test Case    ${TESTNAME}

From variable file
    Check Test Case    ${TESTNAME}

From keyword return value
    Check Test Case    ${TESTNAME}

Escaped dict
    Check Test Case    ${TESTNAME}

Escaped items in dict
    Check Test Case    ${TESTNAME}

Multiple dict variables
    Check Test Case    ${TESTNAME}

Multiple dict variables with same names multiple times
    Check Test Case    ${TESTNAME}

Internal variables
    Check Test Case    ${TESTNAME}

Extended variables
    Check Test Case    ${TESTNAME}

Converted to string if not alone
    Check Test Case    ${TESTNAME}

Non-existing
    Check Test Case    ${TESTNAME}

Non-dictionary
    Check Test Case    ${TESTNAME}

Non-string keys
    Check Test Case    ${TESTNAME}
