*** Settings ***
Suite Setup      Run Tests    --pythonpath ${DATADIR}/keywords    keywords/dots_in_keyword_name.robot
Resource         atest_resource.robot

*** Test Cases ***
Dots in keywords in same file
    Check Test Case    ${TESTNAME}

Dots in keywords in resource file
    Check Test Case    ${TESTNAME}

Dots in keywords in resource file with full name
    Check Test Case    ${TESTNAME}

Dots in keywords in library
    Check Test Case    ${TESTNAME}

Dots in keywords in library with full name
    Check Test Case    ${TESTNAME}

Dots in resource name
    Check Test Case    ${TESTNAME}

Dots in resource name with full name
    Check Test Case    ${TESTNAME}

Dots in resource name and keyword name
    Check Test Case    ${TESTNAME}

Dots in resource name and keyword name with full name
    Check Test Case    ${TESTNAME}

Dots in library name
    Check Test Case    ${TESTNAME}

Dots in library name with full name
    Check Test Case    ${TESTNAME}

Dots in library name and keyword name
    Check Test Case    ${TESTNAME}

Dots in library name and keyword name with full name
    Check Test Case    ${TESTNAME}

Conflicting names with dots
    ${tc} =    Check Test Case    ${TESTNAME}
    Check log message    ${tc.kws[0].msgs[0]}    Running keyword 'Conflict'.
    Check log message    ${tc.kws[1].msgs[0]}    Executing keyword 'In.name.conflict'.
