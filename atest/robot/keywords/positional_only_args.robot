*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/positional_only_args.robot
Resource          atest_resource.robot

*** Test Cases ***
Normal usage
    Check Test Case    ${TESTNAME}

Default values
    Check Test Case    ${TESTNAME}

Positional only value can contain '=' without it being considered named argument
    Check Test Case    ${TESTNAME}

Name of positional only argument can be used with kwargs
    Check Test Case    ${TESTNAME}

Type conversion
    Check Test Case    ${TESTNAME}

Too few arguments
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Too many arguments
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3
