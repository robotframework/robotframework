*** Settings ***
Force Tags      pybot  jybot  regression
Resource        atest_resource.robot

*** Test Cases ***
Exit On Failure
    [Setup]  Run Tests  --runmode exitonfailure  misc/pass_and_fail.robot  misc/suites  running/fatal_exception/02__irrelevant.robot
    Check Test Case  Pass
    Check Test Case  Fail
    Check Test Case  SubSuite1 First  FAIL  Critical failure occurred and exit-on-failure mode is in use.
    Check Test Case  Suite3 First  FAIL  Critical failure occurred and exit-on-failure mode is in use.

Imports Are Skipped On Exit
    Previous test should have passed  Exit On Failure
    Length Should Be  ${ERRORS.msgs}  1

Correct Suite Teardown Is Executed When Exitonfailure Is Used
    [Setup]  Run Tests  --runmode exitonfailure  misc/suites
    ${tsuite} =  Get Test Suite  Suites
    Should Be Equal  ${tsuite.teardown.name}  BuiltIn.Log
    ${tsuite} =  Get Test Suite  Fourth
    Should Be Equal  ${tsuite.teardown.name}  BuiltIn.Log
    ${tsuite} =  Get Test Suite  Tsuite3
    Should Be Equal  ${tsuite.teardown}  ${None}

Exit On Failure With Skip Teardown On Exit
    [Setup]  Run Tests  --runmode ExitOnFailure --runmode SkipTeardownOnExit  misc/suites
    ${tcase} =  Check Test Case  Suite4 First
    Should Be Equal  ${tcase.teardown}  ${None}
    ${tsuite} =  Get Test Suite  Fourth
    Should Be Equal  ${tsuite.teardown}  ${None}
    Check Test Case  SubSuite1 First  FAIL  Critical failure occurred and exit-on-failure mode is in use.
    Check Test Case  Suite3 First  FAIL  Critical failure occurred and exit-on-failure mode is in use.
