*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/remove_from_string.robot
Resource          atest_resource.robot

*** Test Cases ***
Remove String
    Check Test Case    ${TESTNAME}

Remove String Non-ASCII characters
    Check Test Case    ${TESTNAME}

Remove String Not Found
    Check Test Case    ${TESTNAME}

Remove String Multiple Removables
    Check Test Case    ${TESTNAME}

Remove String Using Regexp
    Check Test Case    ${TESTNAME}

Remove String Using Regexp Not Found
    Check Test Case    ${TESTNAME}

Remove String Using Regexp Multiple Patterns
    Check Test Case    ${TESTNAME}
