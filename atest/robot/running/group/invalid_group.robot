*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/group/invalid_group.robot
Resource          atest_resource.robot

*** Test Cases ***
END missing
    Check Test Case    ${TESTNAME}

Empty GROUP
    Check Test Case    ${TESTNAME}

Multiple Parameters
    Check Test Case    ${TESTNAME}

Non existing var in Name
    Check Test Case    ${TESTNAME}
