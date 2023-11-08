*** Settings ***
Suite Setup       Run Tests    --listener ${LISTENER DIR}/v3.py -l l -r r -b d -x x    misc/pass_and_fail.robot
Resource          listener_resource.robot

*** Variables ***
${SEPARATOR}      ${EMPTY + '-' * 78}

*** Test Cases ***
New tests and keywords can be added
    ${tc} =    Check test case    Added by start_suite [start suite]   FAIL    [start] [end]
    Check keyword data    ${tc.kws[0]}    BuiltIn.No Operation
    ${tc} =    Check test case    Added by startTest    PASS    Dynamically added! [end]
    Check keyword data    ${tc.kws[0]}    BuiltIn.Fail    args=Dynamically added!    status=FAIL
    ${tc} =    Check test case    Added by end_Test    FAIL    [start] [end]
    Check keyword data    ${tc.kws[0]}    BuiltIn.Log    args=Dynamically added!, INFO
    Stdout Should Contain    SEPARATOR=\n
    ...    Added by start_suite [start suite] :: [start suite] ${SPACE*17} | FAIL |
    ...    [start] [end]
    ...    ${SEPARATOR}
    ...    Added by startTest ${SPACE*50} | PASS |
    ...    Dynamically added! [end]
    ...    ${SEPARATOR}
    ...    Added by end_test :: Dynamic ${SPACE*40} | FAIL |
    ...    [start] [end]
    ...    ${SEPARATOR}

Test status and message can be changed
    Check Test case    Pass [start suite]    FAIL    [start] [end]
    Check Test case    Fail [start suite]    PASS    Expected failure [end]
    Stdout Should Contain    SEPARATOR=\n
    ...    Pass [start suite] :: [start suite] ${SPACE*33} | FAIL |
    ...    [start] [end]
    Stdout Should Contain    SEPARATOR=\n
    ...    Fail [start suite] :: FAIL Expected failure [start suite] ${SPACE*11} | PASS |
    ...    Expected failure [end]

Changing test status in end suite changes console output, but not output.xml
    Stdout Should Contain     SEPARATOR=\n
    ...    5 tests, 5 passed, 0 failed
    ${from output.xml} =    Catenate    SEPARATOR=\n
    ...    5 tests, 2 passed, 3 failed
    Should be equal    ${SUITE.stat_message}     ${from output.xml}

Test tags can be modified
    Check Test Tags    Fail [start suite]    [end]  [start]  [start suite]  fail  force

Metadata can be modified
    Should be equal    ${SUITE.metadata['suite']}   [start] [end]
    Should be equal    ${SUITE.metadata['tests']}   xxxxx

Changing current element name is not possible
    [Documentation]    But start_suite can change test names
    Should be equal    ${SUITE.name}    Pass And Fail
    Stdout Should Contain    Pass And Fail :: Some tests here
    Stdout Should Contain    Pass [start suite] ::
    Should be equal   ${SUITE.tests[0].name}    Pass [start suite]

Changing current element docs does not change console output, but does change output.xml
    [Documentation]    But start_suite can change test docs
    Stdout Should Contain    Pass And Fail :: Some tests here
    Should be equal    ${SUITE.doc}    Some tests here [start suite] [end suite]
    Stdout Should Contain    Pass [start suite] :: [start suite] ${SPACE*33} | FAIL |
    Check Test Doc    Pass [start suite]    [start suite] [start test] [end test]

Log messages and timestamps can be changed
    ${tc} =   Get test case    Pass [start suite]
    Check log message    ${tc.kws[0].kws[0].msgs[0]}    HELLO SAYS "PASS"!
    Should be equal    ${tc.kws[0].kws[0].msgs[0].timestamp}    ${datetime(2015, 12, 16, 15, 51, 20, 141000)}

Syslog messages can be changed
    Syslog Should Contain Match    2015-12-16 15:51:20.141000 | INFO \ | TESTS EXECUTION ENDED. STATISTICS:

File methods and close are called
    Stderr Should Be Equal To    SEPARATOR=\n
    ...    Debug: d.txt
    ...    Output: output.xml
    ...    Xunit: x.xml
    ...    Log: l.html
    ...    Report: r.html
    ...    Close\n
