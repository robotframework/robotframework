*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/positional_only_args.robot
Force Tags        require-py3.8
Resource          atest_resource.robot

*** Test Cases ***
Normal usage
    Check Test Case    ${TESTNAME}

Named syntax is not used
    Check Test Case    ${TESTNAME}

Default values
    Check Test Case    ${TESTNAME}

Type conversion
    Check Test Case    ${TESTNAME}

Too few arguments
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Too many arguments
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Named argument syntax doesn't work after valid named arguments
    Check Test Case    ${TESTNAME}

Name can be used with kwargs
    Check Test Case    ${TESTNAME}

Mandatory positional-only missing with kwargs
    Check Test Case    ${TESTNAME}
