*** Settings ***
Suite Setup       Run Tests    sources=standard_libraries/builtin/should_match.robot
Resource          builtin_resource.robot

*** Test Cases ***
Should Match
    Check test case    ${TESTNAME}

Should Match with extra trailing newline
    Check test case    ${TESTNAME}

Should Match case-insensitive
    Check test case    ${TESTNAME}

Should Match does not work with bytes
    Check test case    ${TESTNAME}

Should Not Match
    Check test case    ${TESTNAME}

Should Not Match case-insensitive
    Check test case    ${TESTNAME}

Should Match Regexp
    Check test case    ${TESTNAME}

Should Match Regexp returns match and groups
    Check test case    ${TESTNAME}

Should Match Regexp with bytes containing non-ascii characters
    Check test case    ${TESTNAME}

Should Not Match Regexp
    Check test case    ${TESTNAME}
