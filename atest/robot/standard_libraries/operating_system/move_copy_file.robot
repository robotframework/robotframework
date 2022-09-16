*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/move_copy_file.robot
Resource          atest_resource.robot

*** Variables ***
${SAME FILE}      Source '*' and destination '*' point to the same file.

*** Test Cases ***
Move File
    Check Test Case    ${TESTNAME}

Copy File
    Check Test Case    ${TESTNAME}

Copy File With Glob Pattern
    Check Test Case    ${TESTNAME}

Move File With Glob Pattern
    Check Test Case    ${TESTNAME}

Move File With Glob Pattern With Multiple Matches Fails
    Check Test Case    ${TESTNAME}

Copy File With Glob Pattern With Multiple Matches Fails
    Check Test Case    ${TESTNAME}

Copy File With Glob Pattern With No Matches Fails
    Check Test Case    ${TESTNAME}

Move File With Glob Pattern With No Matches Fails
    Check Test Case    ${TESTNAME}

Copy File when destination exists should be ok
    Check Test Case    ${TESTNAME}

Copy File when destination is a directory
    Check Test Case    ${TESTNAME}

Copy File when destination is a directory and file with same name exists
    Check Test Case    ${TESTNAME}

Move File To Existing Directory
    Check Test Case    ${TESTNAME}

Move File To Non-Existing Directory
    Check Test Case    ${TESTNAME}

Move File Using Just File Name
    Check Test Case    ${TESTNAME}

Moving Non-Existing File Fails
    Check Test Case    ${TESTNAME}

Name Contains Glob
    Check Test Case    ${TESTNAME}

Copy File to same path
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    ${SAME FILE}    pattern=True    html=True

Move File to same path
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    ${SAME FILE}    pattern=True    html=True

Copy File to same directory
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    ${SAME FILE}    pattern=True    html=True

Move File to same directory
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    ${SAME FILE}    pattern=True    html=True

Copy File to same path with different case on Windows
    [Tags]    require-windows
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    ${SAME FILE}    pattern=True    html=True

Move File to same path with different case on Windows
    [Tags]    require-windows
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    ${SAME FILE}    pattern=True    html=True

Copy File to same path when file doesn't exist
    Check Test Case    ${TESTNAME}

Move File to same path when file doesn't exist
    Check Test Case    ${TESTNAME}

Move File returns destination path
    Check Test Case    ${TESTNAME}

Copy File returns destination path
    Check Test Case    ${TESTNAME}

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
