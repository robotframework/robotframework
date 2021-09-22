*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/should_be.robot
Resource          atest_resource.robot

*** Test Cases ***
Should Be String Positive
    Check Test Case    ${TESTNAME}

Should Be String Negative
    Check Test Case    ${TESTNAME}

Bytes are not strings
    Check Test Case    ${TESTNAME}

Should Not Be String Positive
    Check Test Case    ${TESTNAME}

Should Not Be String Negative
    Check Test Case    ${TESTNAME}

Should Be Unicode String Positive
    Check Test Case    ${TESTNAME}

Should Be Unicode String Negative
    Check Test Case    ${TESTNAME}

Should Be Byte String Positive
    Check Test Case    ${TESTNAME}

Should Be Byte String Negative
    Check Test Case    ${TESTNAME}

Should Be Lower Case Positive
    Check Test Case    ${TESTNAME}

Should Be Lower Case Negative
    Check Test Case    ${TESTNAME}

Should Be Upper Case Positive
    Check Test Case    ${TESTNAME}

Should Be Upper Case Negative
    Check Test Case    ${TESTNAME}

Should Be Title Case Positive
    Check Test Case    ${TESTNAME}

Should Be Title Case Negative
    Check Test Case    ${TESTNAME}

Should Be Title Case With Excludes
    Check Test Case    ${TESTNAME}

Should Be Title Case With Regex Excludes
    Check Test Case    ${TESTNAME}

Should Be Title Case Does Not Work With ASCII Bytes
    Check Test Case    ${TESTNAME}

Should Be Title Case Does Not Work With Non-ASCII Bytes
    Check Test Case    ${TESTNAME}
