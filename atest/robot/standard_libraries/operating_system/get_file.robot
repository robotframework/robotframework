*** Settings ***
Suite Setup       Run Tests
...    -v SYSTEM_ENCODING:${SYSTEM_ENCODING} -v CONSOLE_ENCODING:${CONSOLE_ENCODING}
...    standard_libraries/operating_system/get_file.robot
Resource          atest_resource.robot

*** Test Cases ***
Get File
    ${tc} =    Check testcase    ${TESTNAME}
    ${path} =    Join Path    %{TEMPDIR}    robot-os-tests    f1.txt
    Check Log Message    ${tc.kws[1].msgs[0]}    Getting file '<a href="file://${path}">${path}</a>'.    HTML

Get File With Non-ASCII Name
    Check testcase    ${TESTNAME}

Get File With Space In Name
    Check testcase    ${TESTNAME}

Get Utf-8 File
    Check testcase    ${TESTNAME}

Get Ascii File With Default Encoding
    Check testcase    ${TESTNAME}

Get Latin-1 With Default Encoding
    Check testcase    ${TESTNAME}

Get Latin-1 With Latin-1 Encoding
    Check testcase    ${TESTNAME}

Get file with system encoding
    Check testcase    ${TESTNAME}

Get file with console encoding
    Check testcase    ${TESTNAME}

Get Utf-16 File with Default Encoding
    Check testcase    ${TESTNAME}

Get File with 'ignore' Error Handler
    Check testcase    ${TESTNAME}

Get File with 'replace' Error Handler
    Check testcase    ${TESTNAME}

Get file converts CRLF to LF
    Check testcase    ${TESTNAME}

Log File
    ${tc}=    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[1]}    hello world\nwith two lines

Log Latin-1 With Latin-1 Encoding
    ${tc} =    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Hyvää üötä

Log File with 'ignore' Error Handler
    ${tc}=    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    Hyv t

Log File with 'replace' Error Handler
    ${tc}=    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    Hyv\ufffd\ufffd \ufffd\ufffdt\ufffd

Get Binary File preserves CRLF line endings
    Check testcase    ${TESTNAME}

Get Binary File returns bytes as-is
    Check testcase    ${TESTNAME}

Grep File
    ${tc}=    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    5 out of 5 lines matched
    Check Log Message    ${tc.kws[1].kws[0].msgs[1]}    2 out of 5 lines matched
    Check Log Message    ${tc.kws[2].kws[0].msgs[1]}    1 out of 5 lines matched
    Check Log Message    ${tc.kws[3].kws[0].msgs[1]}    0 out of 5 lines matched
    Check Log Message    ${tc.kws[4].kws[0].msgs[1]}    3 out of 5 lines matched
    Check Log Message    ${tc.kws[5].kws[0].msgs[1]}    3 out of 5 lines matched
    Check Log Message    ${tc.kws[6].kws[0].msgs[1]}    1 out of 5 lines matched
    Check Log Message    ${tc.kws[7].kws[0].msgs[1]}    4 out of 5 lines matched
    Check Log Message    ${tc.kws[8].kws[0].msgs[1]}    2 out of 5 lines matched
    Check Log Message    ${tc.kws[9].kws[0].msgs[1]}    1 out of 5 lines matched

Grep File with empty file
    ${tc}=    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[1].kws[0].msgs[1]}    0 out of 0 lines matched

Grep File non Ascii
    ${tc}=    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    1 out of 5 lines matched
    Check Log Message    ${tc.kws[1].kws[0].msgs[1]}    1 out of 5 lines matched

Grep File with UTF-16 files
    ${tc}=    Check testcase    ${TESTNAME}
    Log    ${tc.kws[0].kws[0].msgs}
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    3 out of 4 lines matched
    Check Log Message    ${tc.kws[1].kws[0].msgs[1]}    1 out of 2 lines matched
    Check Log Message    ${tc.kws[2].kws[0].msgs[1]}    4 out of 5 lines matched
    Check Log Message    ${tc.kws[3].kws[0].msgs[1]}    2 out of 3 lines matched

Grep file with system encoding
    Check testcase    ${TESTNAME}

Grep file with console encoding
    Check testcase    ${TESTNAME}

Grep File with 'ignore' Error Handler
    ${tc}=    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    1 out of 5 lines matched

Grep File with 'replace' Error Handler
    ${tc}=    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    1 out of 5 lines matched

Grep File With Windows line endings
    ${tc}=    Check testcase    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    1 out of 5 lines matched
