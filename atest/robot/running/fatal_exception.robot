*** Settings ***
Resource          atest_resource.robot

*** Test Cases ***
Exit From Python Keyword
    Run Tests    ${EMPTY}    running/fatal_exception/01__python_library_kw.robot
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown.msgs[0]}    This should be executed
    Check Test Case    Test That Should Not Be Run 1

Exit From Java Keyword
    [Tags]    require-jython
    Run Tests    ${EMPTY}    running/fatal_exception/03__java_library_kw.robot
    Check Test Case    ${TESTNAME}
    Check Test Case    Test That Should Not Be Run 3

Multiple Suite Aware Exiting
    Run Tests    ${EMPTY}    running/fatal_exception/
    Check Test Case    Exit From Python Keyword
    Check Test Case    Test That Should Not Be Run 1
    Check Test Case    Test That Should Not Be Run 2.1
    Check Test Case    Test That Should Not Be Run 2.2

Skip Imports On Exit
    Previous test should have passed    Multiple Suite Aware Exiting
    Should be empty    ${ERRORS.messages}

Skipped tests get robot:exit tag
    Previous test should have passed    Skip Imports On Exit
    Check Test Tags    Exit From Python Keyword    some tag
    Check Test Tags    Test That Should Not Be Run 1    robot:exit
    Check Test Tags    Test That Should Not Be Run 2.1    robot:exit
    Check Test Tags    Test That Should Not Be Run 2.2    robot:exit
    Check Test Tags    Test That Should Not Be Run 3    robot:exit    foo

Skipping creates 'NOT robot:exit' combined tag statistics
    Previous test should have passed    Skipped tests get robot:exit tag
    ${stats} =    Get Element    ${OUTFILE}    statistics/tag
    Should be equal    ${stats[0].text}    NOT robot:exit
    Should be equal    ${stats[0].attrib['pass']}    0
    Should be equal    ${stats[0].attrib['fail']}    1

Multiple Suite Aware Exiting From Suite Setup
    Run Tests    ${EMPTY}    running/fatal_exception_suite_setup/
    Check Test Case    Test That Should Not Be Run 1
    ${ts1} =    Get Test Suite    Suite Setup
    Should End With    ${ts1.teardown.msgs[0].message}    Tearing down 1
    Check Test Case    Test That Should Not Be Run 2.1
    Check Test Case    Test That Should Not Be Run 2.2
    ${ts2} =    Get Test Suite    Irrelevant
    Should Be Equal    ${ts2.teardown}    ${None}

Multiple Suite Aware Exiting From Suite Setup With Skip Teardowns
    Run Tests    --SkipTeardownOnExit    running/fatal_exception_suite_setup/
    Check Test Case    Test That Should Not Be Run 1
    ${ts1} =    Get Test Suite    Suite Setup
    Should Be Equal    ${ts1.teardown}    ${None}
    Check Test Case    Test That Should Not Be Run 2.1
    Check Test Case    Test That Should Not Be Run 2.2
    ${ts2} =    Get Test Suite    Irrelevant
    Should Be Equal    ${ts2.teardown}    ${None}

Fatal Exception and Exit on Failure
    Run Tests    --exitonfailure    running/fatal_exception/01__python_library_kw.robot
    Check Test Case    Test That Should Not Be Run 1    FAIL    Critical failure occurred and exit-on-failure mode is in use.

Fatal Exception And Skip Teardown On Exit
    Run Tests    --SkipTeardownOnExit    running/fatal_exception
    ${tc} =    Check Test Case    Exit From Python Keyword
    Should Be Equal    ${tc.teardown}    ${None}
    ${ts} =    Get Test Suite    Python Library Kw
    Should Be Equal    ${ts.teardown}    ${None}
