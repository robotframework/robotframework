*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/standard_generics.robot
Force Tags        require-py3.9
Resource          atest_resource.robot

*** Test Cases ***
List
    Check Test Case    ${TESTNAME}

Incompatible list
    Check Test Case    ${TESTNAME}

Tuple
    Check Test Case    ${TESTNAME}

Homogenous tuple
    Check Test Case    ${TESTNAME}

Incompatible tuple
    Check Test Case    ${TESTNAME}

Dict
    Check Test Case    ${TESTNAME}

Incompatible dict
    Check Test Case    ${TESTNAME}

Set
    Check Test Case    ${TESTNAME}

Incompatible set
    Check Test Case    ${TESTNAME}

Invalid list
    Check Test Case    ${TESTNAME}

Invalid tuple
    Check Test Case    ${TESTNAME}

Invalid dict
    Check Test Case    ${TESTNAME}

Invalid set
    Check Test Case    ${TESTNAME}
