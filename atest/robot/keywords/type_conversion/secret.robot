*** Settings ***
Suite Setup       Run Tests    --variable "CLI: Secret:From command line"    keywords/type_conversion/secret.robot
Resource          atest_resource.robot

*** Test Cases ***
Command line
    Check Test Case    ${TESTNAME}

Variable section: Scalar
    Check Test Case    ${TESTNAME}

Variable section: List
    Check Test Case    ${TESTNAME}

Variable section: Dict
    Check Test Case    ${TESTNAME}

VAR: Env variable
    Check Test Case    ${TESTNAME}

Create: List
    Check Test Case    ${TESTNAME}

Create: List by extending
    Check Test Case    ${TESTNAME}
Create: Dictionary
    Check Test Case    ${TESTNAME}

Return value: Library keyword
    Check Test Case    ${TESTNAME}

Return value: User keyword
    Check Test Case    ${TESTNAME}

User keyword: Receive not secret
    Check Test Case    ${TESTNAME}

User keyword: Receive not secret var
    Check Test Case    ${TESTNAME}

Library keyword
    Check Test Case    ${TESTNAME}

Library keyword: not secret
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
