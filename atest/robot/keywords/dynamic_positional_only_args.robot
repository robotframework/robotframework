*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/dynamic_positional_only_args.robot
Force Tags        require-py3.8
Resource          atest_resource.robot

*** Test Cases ***
One Argument
    Check Test Case    ${TESTNAME}

Three arguments
    Check Test Case    ${TESTNAME}

Pos and named
    Check Test Case    ${TESTNAME}

Pos and names too few arguments
    Check Test Case    ${TESTNAME}

Three arguments too many arguments
    Check Test Case    ${TESTNAME}

Pos with default
    Check Test Case    ${TESTNAME}

All args
    Check Test Case    ${TESTNAME}

Arg with too may / separators
    Check Test Case    ${TESTNAME}
