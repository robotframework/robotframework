*** Settings ***
Documentation     Tests for registering own run keyword variant
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_variants_registering.robot
Resource          atest_resource.robot

*** Test Cases ***
Not registered Keyword Fails With Content That Should Not Be Evaluated Twice
    Check Test Case    ${TESTNAME}

Registered Function
    Check Test Case    ${TESTNAME}

Registered Method
    Check Test Case    ${TESTNAME}

With Name And Args To Process Registered Method
    Check Test Case    ${TESTNAME}

Registered Keyword With With Name
    Check Test Case    ${TESTNAME}

Registered Keyword From Dynamic Library
    Check Test Case    ${TESTNAME}
