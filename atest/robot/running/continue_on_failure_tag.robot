*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/continue_on_failure_tag.robot
Resource          atest_resource.robot

*** Test Cases ***
Continue in test with tag
    Check Test Case    ${TESTNAME}

Continue in test with Set Tags
    Check Test Case    ${TESTNAME}

Continue in user keyword with tag
    Check Test Case    ${TESTNAME}

Continue in test with tag and UK without tag
    Check Test Case    ${TESTNAME}

Continue in test with tag and nested UK with and without tag
    Check Test Case    ${TESTNAME}

Continue in test with tag and two nested UK with tag
    Check Test Case    ${TESTNAME}

Continue in FOR loop with tag
    Check Test Case    ${TESTNAME}

Continue in FOR loop with Set Tags
    Check Test Case    ${TESTNAME}

No continue in FOR loop without tag
    Check Test Case    ${TESTNAME}

Continue in FOR loop in UK with tag
    Check Test Case    ${TESTNAME}

Continue in FOR loop in UK without tag
    Check Test Case    ${TESTNAME}

Continue in IF with tag
    Check Test Case    ${TESTNAME}

Continue in IF with set and remove tag
    Check Test Case    ${TESTNAME}

No continue in IF without tag
    Check Test Case    ${TESTNAME}

Continue in IF in UK with tag
    Check Test Case    ${TESTNAME}

No continue in IF in UK without tag
    Check Test Case    ${TESTNAME}

Continue in Run Keywords with tag
    Check Test Case    ${TESTNAME}

Recursive continue in test with tag and two nested UK without tag
    Check Test Case    ${TESTNAME}

Recursive continue in test with Set Tags and two nested UK without tag
    Check Test Case    ${TESTNAME}

Recursive continue in test with tag and two nested UK with and without tag
    Check Test Case    ${TESTNAME}

Recursive continue in user keyword
    Check Test Case    ${TESTNAME}

Recursive continue in nested keyword
    Check Test Case    ${TESTNAME}
