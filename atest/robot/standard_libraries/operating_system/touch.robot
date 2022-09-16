*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/touch.robot
Resource          atest_resource.robot

*** Variables ***
${TESTFILE}       %{TEMPDIR}${/}robot-os-tests${/}f1.txt

*** Test Cases ***
Touch Non-Existing File
    ${tc} =    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Touched new file '<a href="file://${TESTFILE}">${TESTFILE}</a>'.    HTML

Touch Existing File
    ${tc} =    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[3].msgs[0]}    Touched existing file '<a href="file://${TESTFILE}">${TESTFILE}</a>'.    HTML
    Check Log Message    ${tc.kws[6].msgs[0]}    Touched existing file '<a href="file://${TESTFILE}">${TESTFILE}</a>'.    HTML

Touch Non-ASCII File
    Check testcase    ${TESTNAME}

Touch File With Space
    Check testcase    ${TESTNAME}

Touching Directory Fails
    Check testcase    ${TESTNAME}

Touch When Parent Does Not Exist Fails
    Check testcase    ${TESTNAME}

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
