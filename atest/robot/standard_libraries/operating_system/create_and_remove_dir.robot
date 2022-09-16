*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/create_and_remove_dir.robot
Resource          atest_resource.robot

*** Test Cases ***
Create Directory
    Check Test Case    ${TESTNAME}

Creating Directory Over Existing File Fails
    Check Test Case    ${TESTNAME}

Remove Directory
    Check Test Case    ${TESTNAME}

Remove Directory Recursively
    Check Test Case    ${TESTNAME}

Removing Non-Existing Directory Is Ok
    Check Test Case    ${TESTNAME}

Removing Non-Empty Directory When Not Recursive Fails
    Check Test Case    ${TESTNAME}

Empty Directory
    Check Test Case    ${TESTNAME}

Emptying Non-Existing Directory Fails
    Check Test Case    ${TESTNAME}

Emptying Dir When Directory Is File Fails
    Check Test Case    ${TESTNAME}

Create And Remove Non-ASCII Directory
    Check Test Case    ${TESTNAME}

Create And Remove Directory With Space
    Check Test Case    ${TESTNAME}

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
