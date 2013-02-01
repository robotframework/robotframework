*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/should_be.txt
Force Tags        pybot    jybot    regression
Resource          atest_resource.txt

*** Test Cases ***
Should Be String Positive
    Check Test Case    ${TESTNAME}

Should Be String Negative
    Check Test Case    ${TESTNAME}

Should Not Be String Positive
    Check Test Case    ${TESTNAME}

Should Not Be String Negative
    Check Test Case    ${TESTNAME}

Should Be Unicode String Positive
    Check Test Case    ${TESTNAME}

Should Be Unicode String Negative
    [Tags]    x-fails-on-ipy
    Check Test Case    ${TESTNAME}

Should Be Byte String Positive
    Check Test Case    ${TESTNAME}

Should Be Byte String Negative
    [Tags]    x-fails-on-ipy
    Check Test Case    ${TESTNAME}

Should Be Lowercase Positive
    Check Test Case    ${TESTNAME}

Should Be Lowercase Negative
    Check Test Case    ${TESTNAME}

Should Be Uppercase Positive
    Check Test Case    ${TESTNAME}

Should Be Uppercase Negative
    Check Test Case    ${TESTNAME}

Should Be Titlecase Positive
    Check Test Case    ${TESTNAME}

Should Be Titlecase Negative
    Check Test Case    ${TESTNAME}

