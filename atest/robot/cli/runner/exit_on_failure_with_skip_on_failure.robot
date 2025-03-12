*** Settings ***
Resource          atest_resource.robot

*** Test Cases ***
Exit-on-failure is not initiated if test fails and skip-on-failure is active
    Run Tests    --exit-on-failure --skip-on-failure skip-on-failure --include skip-on-failure    running/skip/skip.robot
    Should Contain Tests    ${SUITE}
    ...    Skipped with --SkipOnFailure
    ...    Skipped with --SkipOnFailure when failure in setup
    ...    Skipped with --SkipOnFailure when failure in teardown

Exit-on-failure is not initiated if suite setup fails and skip-on-failure is active with all tests
    Run Tests    --exit-on-failure --skip-on-failure tag1 --variable SUITE_SETUP:Fail
    ...    misc/setups_and_teardowns.robot misc/pass_and_fail.robot misc/pass_and_fail.robot
    VAR    ${message}
    ...    Failed test skipped using 'tag1' tag.
    ...
    ...    Original failure:
    ...    Parent suite setup failed:
    ...    AssertionError
    ...    separator=\n
    Should Contain Tests    ${SUITE.suites[0]}
    ...    Test with setup and teardown=SKIP:${message}
    ...    Test with failing setup=SKIP:${message}
    ...    Test with failing teardown=SKIP:${message}
    ...    Failing test with failing teardown=SKIP:${message}
    Should Contain Tests    ${SUITE.suites[1]}
    ...    Pass
    ...    Fail
    Should Contain Tests    ${SUITE.suites[2]}
    ...    Pass=FAIL:Failure occurred and exit-on-failure mode is in use.
    ...    Fail=FAIL:Failure occurred and exit-on-failure mode is in use.

Exit-on-failure is initiated if suite setup fails and skip-on-failure is not active with all tests
    Run Tests    --exit-on-failure --skip-on-failure tag2 --variable SUITE_SETUP:Fail
    ...    misc/setups_and_teardowns.robot misc/pass_and_fail.robot
    VAR    ${prefix}
    ...    Failed test skipped using 'tag2' tag.
    ...
    ...    Original failure:
    ...    separator=\n
    Should Contain Tests    ${SUITE.suites[0]}
    ...    Test with setup and teardown=SKIP:${prefix}\nParent suite setup failed:\nAssertionError
    ...    Test with failing setup=FAIL:Parent suite setup failed:\nAssertionError
    ...    Test with failing teardown=SKIP:${prefix}\nFailure occurred and exit-on-failure mode is in use.
    ...    Failing test with failing teardown=SKIP:${prefix}\nFailure occurred and exit-on-failure mode is in use.
    Should Contain Tests    ${SUITE.suites[1]}
    ...    Pass=FAIL:Failure occurred and exit-on-failure mode is in use.
    ...    Fail=FAIL:Failure occurred and exit-on-failure mode is in use.
