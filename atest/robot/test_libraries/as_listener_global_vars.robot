*** Settings ***
Resource      atest_resource.robot

*** Test Cases ***
Global variables in listener 'close' method when library has test case scope
    [Setup]    Run Tests    ${EMPTY}    test_libraries/as_listener/global_vars_listener/test_case_scope.robot
    Stderr Should Be Equal To    SEPARATOR=\n
        ...  \${SUITE_NAME}: Test Case Scope
        ...  \${SUITE_DOCUMENTATION}: Test global variables in 'close' listener method with test case scope library
        ...  \${PREV_TEST_NAME}:${SPACE}
        ...  \${PREV_TEST_STATUS}:${SPACE}
        ...  \${LOG_LEVEL}: INFO
        ...  \${SUITE_NAME}: Test Case Scope
        ...  \${SUITE_DOCUMENTATION}: Test global variables in 'close' listener method with test case scope library
        ...  \${PREV_TEST_NAME}: Global variables test case scope test 1
        ...  \${PREV_TEST_STATUS}: PASS
        ...  \${LOG_LEVEL}: INFO
        ...  \${SUITE_NAME}: Test Case Scope
        ...  \${SUITE_DOCUMENTATION}: Test global variables in 'close' listener method with test case scope library
        ...  \${PREV_TEST_NAME}: Global variables test case scope test 2
        ...  \${PREV_TEST_STATUS}: PASS
        ...  \${LOG_LEVEL}: INFO\n

Global variables in listener 'close' method when library has test suite scope
    [Setup]    Run Tests    ${EMPTY}    test_libraries/as_listener/global_vars_listener/test_suite_scope_suite
    Stderr Should Be Equal To    SEPARATOR=\n
        ...  \${SUITE_NAME}: Test Suite Scope Suite.Test Suite Scope1
        ...  \${SUITE_DOCUMENTATION}: Test global variables in 'close' listener method with test suite scope library
        ...  \${PREV_TEST_NAME}: Global variables test suite scope test 1
        ...  \${PREV_TEST_STATUS}: PASS
        ...  \${LOG_LEVEL}: INFO
        ...  \${SUITE_NAME}: Test Suite Scope Suite.Test Suite Scope2
        ...  \${SUITE_DOCUMENTATION}: Test global variables in 'close' listener method with test suite scope library
        ...  \${PREV_TEST_NAME}: Global variables test suite scope test 2
        ...  \${PREV_TEST_STATUS}: PASS
        ...  \${LOG_LEVEL}: INFO\n

Global variables in listener 'close' method when library has global scope
    [Setup]    Run Tests    ${EMPTY}    test_libraries/as_listener/global_vars_listener/global_scope_suite
    Stderr Should Be Equal To    SEPARATOR=\n
        ...  \${SUITE_NAME}: Global Scope Suite
        ...  \${SUITE_DOCUMENTATION}:${SPACE}
        ...  \${PREV_TEST_NAME}: Global variables global scope test 2
        ...  \${PREV_TEST_STATUS}: PASS
        ...  \${LOG_LEVEL}: INFO\n