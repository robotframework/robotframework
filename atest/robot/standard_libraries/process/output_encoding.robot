*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/output_encoding.robot
Resource         atest_resource.robot

*** Test Cases ***
Custom encoding when using default streams
    Check Test Case    ${TESTNAME}

Custom encoding when using custom streams
    Check Test Case    ${TESTNAME}

Console encoding
    Check Test Case    ${TESTNAME}

System encoding
    Check Test Case    ${TESTNAME}

Invalid encoding
    Check Test Case    ${TESTNAME}
