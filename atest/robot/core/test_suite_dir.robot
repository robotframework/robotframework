*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  core/test_suite_dir
Resource        atest_resource.robot

*** Variables ***
${1_test_msg}     1 test, 1 passed, 0 failed
${2_test_msg}     2 tests, 2 passed, 0 failed
${3_test_msg}     3 tests, 3 passed, 0 failed

*** Test Cases ***
Main Suite Executed
    Suite Passed  Test Suite Dir  ${3_test_msg}

Child File Suite Executed
    Suite Passed  Test File 1  ${1_test_msg}

Child Dir Suite Executed
    Suite Passed  Test Dir 1  ${2_test_msg}

Grandchild File Suite Executed
    Suite Passed  Test File 2  ${1_test_msg}

Grandchild Dir Suite Executed
    Suite Passed  Test Dir 2  ${1_test_msg}

Grandgrandchild Dir Suite Executed
    Suite Passed  Test Dir 3  ${1_test_msg}

Grandgrandchild File Suite Executed
    Suite Passed  Test File 3  ${1_test_msg}

Child Suites Not Containing Tests Not Executed
    Should Contain Suites    ${SUITE}    Test Dir 1    Test File 1
    Should Contain Suites    ${SUITE.suites[0]}    Test Dir 2    Test File 2
    Should Contain Suites    ${SUITE.suites[1]}
    Should Contain Suites    ${SUITE.suites[0].suites[0]}    Test Dir 3
    Should Contain Suites    ${SUITE.suites[0].suites[0].suites[0]}    Test File 3

File Without Extension
    ${path} =    Normalize Path    ${DATADIR}/core/test_suite_dir/no_extension
    Syslog Should Contain  Ignoring file or directory '${path}'.

File and Directory Starting with _
    ${path} =    Normalize Path    ${DATADIR}/core/test_suite_dir
    Syslog Should Contain  Ignoring file or directory '${path}${/}_ignore_this_file.robot'.
    Syslog Should Contain  Ignoring file or directory '${path}${/}_ignore_this_dir'.

*** Keywords ***
Suite Passed
    [Arguments]  ${name}  ${expected_msg}
    Check Test Suite  ${name}  ${expected_msg}  PASS

Check Sub Suite Count
    [Arguments]  ${name}  ${expected_count}
    ${suite} =  Get Test Suite  ${name}
    Length Should Be  ${suite.suites}  ${expected_count}
