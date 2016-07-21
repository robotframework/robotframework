*** Settings ***
Documentation   Tests for libraries using getKeywordNames and runKeyword functionality. In these tests libraries are implemented with Java.
Suite Setup     Run Tests  ${EMPTY}  test_libraries/dynamic_library_java.robot
Force Tags      require-jython
Resource        atest_resource.robot

*** Test Cases ***
Run Keyword
    Check Test Case  ${TESTNAME}

Run Keyword But No Get Keyword Names
    Check Test Case  ${TESTNAME}

Not Found Keyword
    Check Test Case  ${TESTNAME}

Can use lists instead of arrays in dynamic API
    Check Test Case  ${TESTNAME}

