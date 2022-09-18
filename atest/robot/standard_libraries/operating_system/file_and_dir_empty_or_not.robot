*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/file_and_dir_empty_or_not.robot
Resource          atest_resource.robot

*** Test Cases ***
Directory Should Be Empty
    Check testcase    ${TESTNAME}

Non-ASCII Directory Should Be Empty
    Check testcase    ${TESTNAME}

Directory With Space Should Be Empty
    Check testcase    ${TESTNAME}

Directory Should Be Empty When Directory Does Not Exist
    Check testcase    ${TESTNAME}

Directory Should Not Be Empty
    Check testcase    ${TESTNAME}

Non-ASCII Directory Should Not Be Empty
    Check testcase    ${TESTNAME}

Directory With Space Should Not Be Empty
    Check testcase    ${TESTNAME}

Directory Should Not Be Empty When Directory Does Not Exist
    Check testcase    ${TESTNAME}

File Should Be Empty
    Check testcase    ${TESTNAME}

Non-ASCII File Should Be Empty
    Check testcase    ${TESTNAME}

File With Space Should Be Empty
    Check testcase    ${TESTNAME}

File Should Be Empty When File Does Not Exist
    Check testcase    ${TESTNAME}

File Should Not Be Empty
    Check testcase    ${TESTNAME}

Non-ASCII File Should Not Be Empty
    Check testcase    ${TESTNAME}

File With Space Should Not Be Empty
    Check testcase    ${TESTNAME}

File Should Not Be Empty When File Does Not Exist
    Check testcase    ${TESTNAME}

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
