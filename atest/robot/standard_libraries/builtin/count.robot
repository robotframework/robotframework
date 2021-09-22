*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/count.robot
Resource          builtin_resource.robot

*** Test Cases ***
Get Count
    [Documentation]    Tested also by Should Contain X Times keyword that uses this intenally.
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Item found from container 2 times.
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    Item found from container 2 times.
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    Item found from container 1 time.
    Check Log Message    ${tc.kws[3].kws[0].msgs[0]}    Item found from container 1 time.
    Check Log Message    ${tc.kws[4].kws[0].msgs[0]}    Item found from container 50 times.
    Check Log Message    ${tc.kws[5].kws[0].msgs[0]}    Item found from container 0 times.

Should Contain X Times with strings
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Item found from container 2 times.
    Check Log Message    ${tc.kws[1].msgs[0]}    Item found from container 1 time.
    Check Log Message    ${tc.kws[3].msgs[0]}    Item found from container 0 times.

Should Contain X Times with containers
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Item found from container 1 time.
    Check Log Message    ${tc.kws[1].msgs[0]}    Item found from container 2 times.
    Check Log Message    ${tc.kws[3].msgs[0]}    Item found from container 0 times.

Should Contain X Times failing
    Check test case    ${TESTNAME}

Should Contain X Times case-insensitive
    Check test case    ${TESTNAME}

Should Contain X Times without leading spaces
    Check test case    ${TESTNAME}

Should Contain X Times without trailing spaces
    Check test case    ${TESTNAME}

Should Contain X Times without leading and trailing spaces
    Check test case    ${TESTNAME}

Should Contain X Times and do not collapse spaces
    Check test case    ${TESTNAME}

Should Contain X Times and collapse spaces
    Check test case    ${TESTNAME}

Should Contain X Times with invalid item
    Check test case    ${TESTNAME}

Should Contain X Times with invalid count
    Check test case    ${TESTNAME}
