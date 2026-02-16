*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/wait_until_removed_created.robot
Resource          atest_resource.robot

*** Test Cases ***
Wait removal when do not exist
    Check Test Case    ${TESTNAME}

Removed before timeout
    Check Test Case    ${TESTNAME}

Removed before timeout when using glob pattern
    Check Test Case    ${TESTNAME}

File not removed before timeout
    Check Test Case    ${TESTNAME}

Directory not removed before timeout
    Check Test Case    ${TESTNAME}

Not removed before timeout when using glob pattern
    Check Test Case    ${TESTNAME}

Wait removal when path itself contains glob charactes
    Check Test Case    ${TESTNAME}

Wait removal when using `pathlib.Path`
    Check Test Case    ${TESTNAME}

None disables remove timeout
    Check Test Case    ${TESTNAME}

Invalid remove timeout
    Check Test Case    ${TESTNAME}

Wait creation when already created
    Check Test Case    ${TESTNAME}

Created before timeout
    Check Test Case    ${TESTNAME}

Created before timeout when using glob pattern
    Check Test Case    ${TESTNAME}

File not created before timeout
    Check Test Case    ${TESTNAME}

Directory not created before timeout
    Check Test Case    ${TESTNAME}

Not created before timeout when using glob pattern
    Check Test Case    ${TESTNAME}

Wait creation when path itself contains glob charactes
    Check Test Case    ${TESTNAME}

Wait creation when using `pathlib.Path`
    Check Test Case    ${TESTNAME}

None disables create timeout
    Check Test Case    ${TESTNAME}

Invalid create timeout
    Check Test Case    ${TESTNAME}
