*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/continue_on_failure_tag.robot
Resource          atest_resource.robot

*** Test Cases ***
Continue in test with continue tag
    Check Test Case    ${TESTNAME}

Continue in test with Set Tags
    Check Test Case    ${TESTNAME}

Continue in user keyword with continue tag
    Check Test Case    ${TESTNAME}

Continue in test with continue tag and UK without tag
    Check Test Case    ${TESTNAME}

Continue in test with continue tag and nested UK with and without tag
    Check Test Case    ${TESTNAME}

Continue in test with continue tag and two nested UK with continue tag
    Check Test Case    ${TESTNAME}

Continue in FOR loop with continue tag
    Check Test Case    ${TESTNAME}

Continue in FOR loop with Set Tags
    Check Test Case    ${TESTNAME}

No continue in FOR loop without tag
    Check Test Case    ${TESTNAME}

Continue in FOR loop in UK with continue tag
    Check Test Case    ${TESTNAME}

Continue in FOR loop in UK without tag
    Check Test Case    ${TESTNAME}

Continue in IF with continue tag
    Check Test Case    ${TESTNAME}

Continue in IF with set and remove tag
    Check Test Case    ${TESTNAME}

No continue in IF without tag
    Check Test Case    ${TESTNAME}

Continue in IF in UK with continue tag
    Check Test Case    ${TESTNAME}

No continue in IF in UK without tag
    Check Test Case    ${TESTNAME}

Continue in Run Keywords with continue tag
    Check Test Case    ${TESTNAME}

Recursive continue in test with continue tag and two nested UK without tag
    Check Test Case    ${TESTNAME}

Recursive continue in test with Set Tags and two nested UK without tag
    Check Test Case    ${TESTNAME}

Recursive continue in test with continue tag and two nested UK with and without tag
    Check Test Case    ${TESTNAME}

Recursive continue in test with continue tag and UK with stop tag
    Check Test Case    ${TESTNAME}

Recursive continue in test with continue tag and UK with recursive stop tag
    Check Test Case    ${TESTNAME}

Recursive continue in user keyword
    Check Test Case    ${TESTNAME}

Recursive continue in nested keyword
    Check Test Case    ${TESTNAME}

stop-on-failure in keyword in Teardown
    Check Test Case    ${TESTNAME}

stop-on-failure with continuable failure in keyword in Teardown
    Check Test Case    ${TESTNAME}

stop-on-failure with run-kw-and-continue failure in keyword in Teardown
    Check Test Case    ${TESTNAME}

stop-on-failure with run-kw-and-continue failure in keyword
    Check Test Case    ${TESTNAME}

Test teardown using run keywords with stop tag in test case
    Check Test Case    ${TESTNAME}

Test teardown using user keyword with recursive stop tag in test case
    Check Test Case    ${TESTNAME}

Test teardown using user keyword with stop tag in test case
    Check Test Case    ${TESTNAME}

Test Teardown with stop tag in user keyword
    Check Test Case    ${TESTNAME}

Test Teardown with recursive stop tag in user keyword
    Check Test Case    ${TESTNAME}

Test Teardown with recursive stop tag and UK with continue tag
    Check Test Case    ${TESTNAME}

Test Teardown with recursive stop tag and UK with recursive continue tag
    Check Test Case    ${TESTNAME}

stop-on-failure with Template
    Check Test Case    ${TESTNAME}

recursive-stop-on-failure with Template
    Check Test Case    ${TESTNAME}

stop-on-failure with Template and Teardown
    Check Test Case    ${TESTNAME}

stop-on-failure does not stop continuable failure in test
    Check Test Case    ${TESTNAME}

Test recursive-continue-recursive-stop
    Check Test Case    ${TESTNAME}

Test recursive-stop-recursive-continue
    Check Test Case    ${TESTNAME}

Test recursive-stop-recursive-continue-recursive-stop
    Check Test Case    ${TESTNAME}

Test test setup with continue-on-failure
    Check Test Case    ${TESTNAME}

Test test setup with recursive-continue-on-failure
    Check Test Case    ${TESTNAME}

recursive-stop-on-failure with continue-on-failure
    Check Test Case    ${TESTNAME}

recursive-continue-on-failure with stop-on-failure
    Check Test Case    ${TESTNAME}
