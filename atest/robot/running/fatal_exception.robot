*** Settings ***
Force Tags      regression
Default Tags    pybot  jybot
Resource        atest_resource.robot

*** Test Cases ***
Exit From Python Keyword
    Run Tests  ${EMPTY}  running/fatal_exception/01__python_library_kw.robot
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.teardown.msgs[0]}  This should be executed
    Check Test Case  Test That Should Not Be Run 1

Exit From Java Keyword
    [tags]  jybot
    Run Tests  ${EMPTY}  running/fatal_exception/03__java_library_kw.robot
    Check Test Case  ${TESTNAME}
    Check Test Case  Test That Should Not Be Run 3

Multiple Suite Aware Exiting
    Run Tests  ${EMPTY}  running/fatal_exception/
    Check Test Case  Exit From Python Keyword
    Check Test Case  Test That Should Not Be Run 1
    Check Test Case  Test That Should Not Be Run 2.1
    Check Test Case  Test That Should Not Be Run 2.2

Skip Imports On Exit
    Previous test should have passed  Multiple Suite Aware Exiting
    Should be empty  ${ERRORS.messages}

Multiple Suite Aware Exiting From Suite Setup
    Run Tests  ${EMPTY}  running/fatal_exception_suite_setup/
    Check Test Case  Test That Should Not Be Run 1
    ${ts1} =  Get Test Suite  Suite Setup
    Should End With  ${ts1.teardown.msgs[0].message}  Tearing down 1
    Check Test Case  Test That Should Not Be Run 2.1
    Check Test Case  Test That Should Not Be Run 2.2
    ${ts2} =  Get Test Suite  Irrelevant
    Should Be Equal  ${ts2.teardown}  ${None}

Multiple Suite Aware Exiting From Suite Setup With Skip Teardowns
    Run Tests  --SkipTeardownOnExit  running/fatal_exception_suite_setup/
    Check Test Case  Test That Should Not Be Run 1
    ${ts1} =  Get Test Suite  Suite Setup
    Should Be Equal  ${ts1.teardown}  ${None}
    Check Test Case  Test That Should Not Be Run 2.1
    Check Test Case  Test That Should Not Be Run 2.2
    ${ts2} =  Get Test Suite  Irrelevant
    Should Be Equal  ${ts2.teardown}  ${None}

Fatal Exception and Runmode Exit on Failure
    Run Tests  --exitonfailure  running/fatal_exception/01__python_library_kw.robot
    Check Test Case  Test That Should Not Be Run 1  FAIL
    ...  Critical failure occurred and exit-on-failure mode is in use.

Fatal Exception and Runmodes Exit On Failure And Skip Teardown On Exit
    Run Tests  --SkipTeardownOnExit  running/fatal_exception
    ${tcase} =  Check Test Case  Exit From Python Keyword
    Should Be Equal  ${tcase.teardown}  ${None}
    ${tsuite}  Get Test Suite  Python Library Kw
    Should Be Equal  ${tsuite.teardown}  ${None}
