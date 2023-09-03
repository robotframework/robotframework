*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/modified_time.robot
Resource          atest_resource.robot

*** Variables ***
${TESTFILE}       %{TEMPDIR}${/}robot-os-tests${/}f1.txt

*** Test Cases ***
Get Modified Time As Timestamp
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Match Regexp    ${tc.kws[0].msgs[0].message}    Last modified time of '<a href=.*</a>' is \\d\\d\\d\\d-\\d\\d-\\d\\d \\d\\d:\\d\\d:\\d\\d

Get Modified Time As Seconds After Epoch
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Match Regexp    ${tc.kws[0].msgs[0].message}    Last modified time of '<a href=.*</a>' is \\d+

Get Modified Time As Parts
    Check Test Case    ${TESTNAME}

Get Modified Time Fails When Path Does Not Exist
    Check Test Case    ${TESTNAME}

Set Modified Time Using Epoch
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[2].msgs[0]}    Set modified time of '<a href="file://${TESTFILE}">${TESTFILE}</a>' to 2018-11-22 13:13:42.    HTML

Set Modified Time Using Timestamp
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[2].kws[0].kws[0].msgs[0]}    Set modified time of '<a href="file://${TESTFILE}">${TESTFILE}</a>' to 2018-11-22 13:13:42.    HTML
    Check Log Message    ${tc.kws[2].kws[1].kws[0].msgs[0]}    Set modified time of '<a href="file://${TESTFILE}">${TESTFILE}</a>' to 2018-11-22 13:13:42.    HTML
    Check Log Message    ${tc.kws[2].kws[2].kws[0].msgs[0]}    Set modified time of '<a href="file://${TESTFILE}">${TESTFILE}</a>' to 2018-11-22 13:13:42.    HTML
    Check Log Message    ${tc.kws[2].kws[3].kws[0].msgs[0]}    Set modified time of '<a href="file://${TESTFILE}">${TESTFILE}</a>' to 2018-11-22 13:13:42.    HTML

Set Modified Time Using Invalid Timestamp
    Check Test Case    ${TESTNAME}

Set Modified Time Using NOW
    Check Test Case    ${TESTNAME}

Set Modified Time Using UTC
    Check Test Case    ${TESTNAME}

Set Modified Time Using NOW + invalid
    Check Test Case    ${TESTNAME}

Set Modified Time Fails When Path Does Not Exist
    Check Test Case    ${TESTNAME}

Set Modified Time Fails When Path Is Directory
    Check Test Case    ${TESTNAME}

Set And Get Modified Time Of Non-ASCII File
    Check Test Case    ${TESTNAME}

Set And Get Modified Time Of File With Spaces In Name
    Check Test Case    ${TESTNAME}

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
