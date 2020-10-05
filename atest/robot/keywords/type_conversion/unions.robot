*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/unions.robot
Resource         atest_resource.robot
Force Tags       require-py3.7

*** Test Cases ***
Union testing
     Check Test Case    ${TESTNAME}

Optional is removed when None is default
     Check Test Case    ${TESTNAME}

Multitype union works in order
     Check Test Case    ${TESTNAME}

Custom type inside of union
     Check Test Case    ${TESTNAME}

Unexpected object is just passed when in union
     Check Test Case    ${TESTNAME}

