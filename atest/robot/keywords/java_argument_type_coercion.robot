*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/java_argument_type_coercion.robot
Force Tags        require-jython
Resource          atest_resource.robot

*** Test Cases ***
Coercing Integer Arguments
    Check Test Case    ${TESTNAME}

Coercing Boolean Arguments
    Check Test Case    ${TESTNAME}

Coercing Real Number Arguments
    Check Test Case    ${TESTNAME}

Coercing Multiple Arguments
    Check Test Case    ${TESTNAME}

Coercing Fails With Conflicting Signatures
    Check Test Case    ${TESTNAME}

It Is Possible To Coerce Only Some Arguments
    Check Test Case    ${TESTNAME}
