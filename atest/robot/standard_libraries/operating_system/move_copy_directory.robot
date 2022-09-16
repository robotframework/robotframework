*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/move_copy_directory.robot
Resource          atest_resource.robot

*** Test Cases ***
Move Directory
    Check Test Case    ${TESTNAME}

Copy Directory
    Check Test Case    ${TESTNAME}

Move Directory To Existing Directory
    Check Test Case    ${TESTNAME}

Copy Directory To Existing Directory
    Check Test Case    ${TESTNAME}

Move Directory To Non-Existing Directory Tree
    Check Test Case    ${TESTNAME}

Copy Directory To Non-Existing Directory Tree
    Check Test Case    ${TESTNAME}

Move Directory Using Just Directory Name
    Check Test Case    ${TESTNAME}

Copy Directory Using Just Directory Name
    Check Test Case    ${TESTNAME}

Moving Non-Existing Directory Fails
    Check Test Case    ${TESTNAME}

Copying Non-Existing Directory Fails
    Check Test Case    ${TESTNAME}

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
