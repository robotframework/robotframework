*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/remove_file.robot
Resource          atest_resource.robot

*** Test Cases ***
Remove File
    Check Test Case    ${TESTNAME}

Remove Files
    Check Test Case    ${TESTNAME}

Remove Non-ASCII File
    Check Test Case    ${TESTNAME}

Remove File With Space
    Check Test Case    ${TESTNAME}

Remove Files Using Glob Pattern
    Check Test Case    ${TESTNAME}

Remove Non-ASCII Files Using Glob Pattern
    [Tags]    no-osx
    # On OSX python glob does not handle NFD characters.
    Check Test Case    ${TESTNAME}

Remove Non-Existing File
    Check Test Case    ${TESTNAME}

Removing Directory As A File Fails
    Check Test Case    ${TESTNAME}

Remove file containing glob pattern
    Check Test Case    ${TESTNAME}
