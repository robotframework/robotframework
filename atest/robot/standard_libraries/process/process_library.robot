*** Settings ***
Documentation    This suite should be split. Please don't add more tests but
...              create a new suite and move related tests from here to it too.
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/process_library.robot
Resource         atest_resource.robot

*** Test Cases ***
Library namespace should be global
    Check Test Case    ${TESTNAME}

Error in exit code and stderr output
    Check Test Case    ${TESTNAME}

Change current working directory
    Check Test Case    ${TESTNAME}

Run process in shell
    Check Test Case    ${TESTNAME}

Get process id
    Check Test Case    ${TESTNAME}
