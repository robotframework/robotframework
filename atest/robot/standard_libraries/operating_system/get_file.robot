*** Settings ***
Suite Setup       Run Tests
...    -v SYSTEM_ENCODING:${SYSTEM_ENCODING} -v CONSOLE_ENCODING:${CONSOLE_ENCODING}
...    standard_libraries/operating_system/get_file.robot
Resource          atest_resource.robot

*** Test Cases ***
Get File
    ${tc} =    Check Test Case    ${TESTNAME}
    ${path} =    Join Path    %{TEMPDIR}    robot-os-tests    f1.txt
    Check Log Message    ${tc[1, 0]}    Getting file '<a href="file://${path}">${path}</a>'.    HTML

Get File With Non-ASCII Name
    Check Test Case    ${TESTNAME}

Get File With Space In Name
    Check Test Case    ${TESTNAME}

Get Utf-8 File
    Check Test Case    ${TESTNAME}

Get Ascii File With Default Encoding
    Check Test Case    ${TESTNAME}

Get Latin-1 With Default Encoding
    Check Test Case    ${TESTNAME}

Get Latin-1 With Latin-1 Encoding
    Check Test Case    ${TESTNAME}

Get file with system encoding
    Check Test Case    ${TESTNAME}

Get file with console encoding
    Check Test Case    ${TESTNAME}

Get Utf-16 File with Default Encoding
    Check Test Case    ${TESTNAME}

Get File with 'ignore' Error Handler
    Check Test Case    ${TESTNAME}

Get File with 'replace' Error Handler
    Check Test Case    ${TESTNAME}

Get file converts CRLF to LF
    Check Test Case    ${TESTNAME}

Log File
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 1]}    hello world\nwith two lines

Log Latin-1 With Latin-1 Encoding
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 1]}    Hyvää üötä

Log File with 'ignore' Error Handler
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1]}    Hyv t

Log File with 'replace' Error Handler
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1]}    Hyv\ufffd\ufffd \ufffd\ufffdt\ufffd

Get Binary File preserves CRLF line endings
    Check Test Case    ${TESTNAME}

Get Binary File returns bytes as-is
    Check Test Case    ${TESTNAME}

Grep File
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1]}    5 out of 5 lines matched.
    Check Log Message    ${tc[1, 0, 1]}    2 out of 5 lines matched.
    Check Log Message    ${tc[2, 0, 1]}    1 out of 5 lines matched.
    Check Log Message    ${tc[3, 0, 1]}    0 out of 5 lines matched.
    Check Log Message    ${tc[4, 0, 1]}    3 out of 5 lines matched.
    Check Log Message    ${tc[5, 0, 1]}    3 out of 5 lines matched.
    Check Log Message    ${tc[6, 0, 1]}    1 out of 5 lines matched.
    Check Log Message    ${tc[7, 0, 1]}    4 out of 5 lines matched.
    Check Log Message    ${tc[8, 0, 1]}    2 out of 5 lines matched.
    Check Log Message    ${tc[9, 0, 1]}    1 out of 5 lines matched.

Grep File with regexp
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1]}    5 out of 5 lines matched.
    Check Log Message    ${tc[1, 0, 1]}    2 out of 5 lines matched.
    Check Log Message    ${tc[2, 0, 1]}    1 out of 5 lines matched.
    Check Log Message    ${tc[3, 0, 1]}    0 out of 5 lines matched.
    Check Log Message    ${tc[4, 0, 1]}    3 out of 5 lines matched.
    Check Log Message    ${tc[5, 0, 1]}    3 out of 5 lines matched.
    Check Log Message    ${tc[6, 0, 1]}    1 out of 5 lines matched.
    Check Log Message    ${tc[7, 0, 1]}    4 out of 5 lines matched.
    Check Log Message    ${tc[8, 0, 1]}    2 out of 5 lines matched.
    Check Log Message    ${tc[9, 0, 1]}    1 out of 5 lines matched.

Grep File with empty file
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0, 1]}    0 out of 0 lines matched.

Grep File non Ascii
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1]}    1 out of 5 lines matched.
    Check Log Message    ${tc[1, 0, 1]}    1 out of 5 lines matched.

Grep File non Ascii with regexp
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1]}    1 out of 5 lines matched.
    Check Log Message    ${tc[1, 0, 1]}    1 out of 5 lines matched.

Grep File with UTF-16 files
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1]}    3 out of 4 lines matched.
    Check Log Message    ${tc[1, 0, 1]}    1 out of 2 lines matched.
    Check Log Message    ${tc[2, 0, 1]}    4 out of 5 lines matched.
    Check Log Message    ${tc[3, 0, 1]}    2 out of 3 lines matched.

Grep file with system encoding
    Check Test Case    ${TESTNAME}

Grep file with console encoding
    Check Test Case    ${TESTNAME}

Grep File with 'ignore' Error Handler
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1]}    1 out of 5 lines matched.

Grep File with 'replace' Error Handler
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1]}    1 out of 5 lines matched.

Grep File With Windows line endings
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1]}    1 out of 5 lines matched.

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
