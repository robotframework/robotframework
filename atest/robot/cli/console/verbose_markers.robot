*** Settings ***
Resource       console_resource.robot
Suite Setup    Run Tests Without Processing Output   --console verbose --consolemarkers on    ${TEST FILE}

*** Variables ***
${TEST FILE}    cli/console/verbose_markers.robot
${SEPARATOR}    -
${KW CONTINUE}  BuiltIn.Run Keyword And Continue On Failure
${KW NOOP}      BuiltIn.No Operation
${KW LOG}       BuiltIn.Log

*** Test Cases ***
Suite Setup
    Check Stdout Contains    SEPARATOR=
    ...    ${TESTNAME}${SPACE * 59}\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    \r${SPACE * 78}\r
    ...    ${TESTNAME}${SPACE * 59}| PASS |\n

Few Pass Markers
    Check Stdout Contains    SEPARATOR=
    ...    ${TESTNAME}${SPACE * 54}\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    \r${SPACE * 78}\r
    ...    ${TESTNAME}${SPACE * 54}| PASS |\n

Few Pass And Fail Markers
    Check Stdout Contains    SEPARATOR=
    ...    ${TESTNAME}${SPACE * 45}\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW CONTINUE}${SPACE * 2}Fail${SPACE * 17}F
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW CONTINUE}${SPACE * 2}Fail${SPACE * 17}| FAIL |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    \r${SPACE * 78}\r
    ...    ${TESTNAME}${SPACE * 45}| FAIL |\n

More Markers Than Fit Into Status Area During Very Deep Keyword
    Check Stdout Contains    SEPARATOR=
    ...    ${TESTNAME}${SPACE * 7}\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}KeywordLevel1${SPACE * 53}........
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}KeywordLevel1${SPACE * 53}........
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}KeywordLevel1${SPACE * 53}......
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}KeywordLevel1${SPACE * 53}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    \r${SPACE * 78}\r
    ...    ${TESTNAME}${SPACE * 7}| PASS |\n

Warnings Are Shown Correctly
    Check Stdout Contains    SEPARATOR=
    ...    ${TESTNAME}${SPACE * 42}\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW LOG}${SPACE * 2}Warning${SPACE * 2}WARN${SPACE * 40}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW LOG}${SPACE * 2}Warning${SPACE * 2}WARN${SPACE * 40}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW LOG}${SPACE * 2}Warning${SPACE * 2}WARN${SPACE * 40}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    \r${SPACE * 78}\r
    ...    ${TESTNAME}${SPACE * 42}| PASS |\n
    Check Stderr Contains    SEPARATOR=\n
    ...    [ WARN ] Warning

Suite Teardown
    Check Stdout Contains    SEPARATOR=
    ...    ${TESTNAME}${SPACE * 56}\n
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}
    ...    \r${SPACE * 78}\r
    ...    ${SPACE * 4}${KW NOOP}${SPACE * 46}| PASS |\n
    ...    \r${SPACE * 78}\r
    ...    ${TESTNAME}${SPACE * 56}| PASS |\n

Verbose Output is Disabled When Markers Are Disabled
    Run Tests And Verify Normal Output When Markers Are Disabled    --console verbose -K OFF

*** Keywords ***
Run Tests And Verify Normal Output When Markers Are Disabled
    [Arguments]    ${opt}
    Run Tests Without Processing Output    ${opt}    ${TEST FILE}
    Check Stdout Contains    SEPARATOR=\n
    ...    Few Pass Markers${SPACE * 54}| PASS |
    ...    ${SEPARATOR * 78}
    ...    Few Pass And Fail Markers${SPACE * 45}| FAIL |
    ...    AssertionError
    ...    ${SEPARATOR * 78}
    ...    More Markers Than Fit Into Status Area During Very Deep Keyword${SPACE * 7}| PASS |
    ...    ${SEPARATOR * 78}
    ...    Warnings Are Shown Correctly${SPACE * 42}| PASS |
    ...    ${SEPARATOR * 78}
    ...    Verbose Markers${SPACE * 55}| FAIL |
