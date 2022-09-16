*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/get_file_size.robot
Resource          atest_resource.robot

*** Variables ***
${TESTFILE}       %{TEMPDIR}${/}robot-os-tests${/}f1.txt
${NONASCII}       %{TEMPDIR}${/}robot-os-tests${/}nön-äscïï
${WITHSPACE}      %{TEMPDIR}${/}robot-os-tests${/}with space

*** Test Cases ***
Get File Size
    ${tc} =    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    Size of file '<a href="file://${TESTFILE}">${TESTFILE}</a>' is 0 bytes.    HTML
    Check Log Message    ${tc.kws[4].msgs[0]}    Size of file '<a href="file://${NONASCII}">${NONASCII}</a>' is 1 byte.    HTML
    Check Log Message    ${tc.kws[7].msgs[0]}    Size of file '<a href="file://${WITHSPACE}">${WITHSPACE}</a>' is 12 bytes.    HTML

Get size of non-existing file
    Check testcase    ${TESTNAME}

Get size of directory
    Check testcase    ${TESTNAME}

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
