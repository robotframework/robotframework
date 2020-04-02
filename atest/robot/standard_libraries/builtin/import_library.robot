*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/import_library.robot
Resource          atest_resource.robot

*** Test Cases ***
Import Library
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3

Import Library With Arguments
    Check Test Case    ${TEST NAME}

Import Library With Variables And WITH NAME
    Check Test Case    ${TEST NAME}

Import Library With WITH NAME containing non-ASCII spaces
    Check Test Case    ${TEST NAME}

Import Library Using Physical Path
    Check Test Case    ${TEST NAME}

Import Library Using Physical Path, Arguments And WITH NAME
    Check Test Case    ${TEST NAME}

Import Library Arguments Are Resolved Only Once
    Check Test Case    ${TEST NAME}

Import Library With Named Arguments
    Check Test Case    ${TEST NAME}

Import Library Failure Is Catchable
    Check Test Case    ${TESTNAME}

Import Library From Path
    Check Test Case    ${TESTNAME}

Extra Spaces In Name Are Not Supported
    Check Test Case    ${TESTNAME}
    Should Be Empty    ${ERRORS}
