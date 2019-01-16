*** Settings ***
Suite Setup       Run Tests    sources=standard_libraries/builtin/should_xxx_with.robot
Resource          builtin_resource.robot

*** Test Cases ***
Should Start With
    Check test case    ${TESTNAME}

Should Start With case-insensitive
    ${tc}=    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    (case insensitive)

Should Start With without values
    Check test case    ${TESTNAME}

Should Not Start With
    Check test case    ${TESTNAME}

Should Not Start With case-insensitive
    ${tc}=    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    (case insensitive)

Should End With
    Check test case    ${TESTNAME}

Should End With case-insensitive
    ${tc}=    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    (case insensitive)

Should End With without values
    Check test case    ${TESTNAME}

Should Not End With
    Check test case    ${TESTNAME}

Should Not End With case-insensitive
    ${tc}=    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    (case insensitive)
