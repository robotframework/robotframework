*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/get_process_result.robot
Resource         atest_resource.robot

*** Test Cases ***
Get whole result object
    Check Test Case    ${TESTNAME}

Get one result attribute
    Check Test Case    ${TESTNAME}

Get two result attribute
    Check Test Case    ${TESTNAME}

Get all result attributes
    Check Test Case    ${TESTNAME}

Get same result multiple times
    Check Test Case    ${TESTNAME}

Get result of active process
    Check Test Case    ${TESTNAME}

Getting results of unfinished processes is not supported
    Check Test Case    ${TESTNAME}
