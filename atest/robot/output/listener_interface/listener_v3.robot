*** Settings ***
Resource    atest_resource.robot
Suite Setup       Run Tests    --listener ${DATADIR}/output/listeners/v3.py -l l -r r -b d -x x   misc/pass_and_fail.robot

*** Test Cases ***
New tests and keywords can be added to suite
   ${tc} =    Check test case    New [start suite]   FAIL    Message: [start] [end]
   Check Stdout Contains    SEPARATOR=\n
   ...    New [start suite] :: [start suite] ${SPACE*34} | FAIL |
   ...    Message: [start] [end]
   Check keyword data    ${tc.kws[0]}    BuiltIn.No Operation

Test status and message can be changed
    Check Test case    Pass [start suite]    FAIL    Message: [start] [end]
    Check Test case    Fail [start suite]    PASS    Expected failure [end]
    Check Stdout Contains    SEPARATOR=\n
    ...    Pass [start suite] :: [start suite] ${SPACE*33} | FAIL |
    ...    Message: [start] [end]
    Check Stdout Contains    SEPARATOR=\n
    ...    Fail [start suite] :: FAIL Expected failure [start suite] ${SPACE*11} | PASS |
    ...    Expected failure [end]

Changing test status in end suite changes console output, but not output.xml
   Check stdout contains     SEPARATOR=\n
   ...    3 critical tests, 3 passed, 0 failed
   ...    3 tests total, 3 passed, 0 failed
   ${from output.xml} =    Catenate    SEPARATOR=\n
   ...    3 critical tests, 1 passed, 2 failed
   ...    3 tests total, 1 passed, 2 failed
   Should be equal    ${SUITE.stat_message}     ${from output.xml}

Test tags can be modified
   Check Test Tags    Fail [start suite]    [end]  [start]  [start suite]  fail  force

Metadata can be modified
   Should be equal    ${SUITE.metadata['suite']}   [start] [end]
   Should be equal    ${SUITE.metadata['tests']}   xxx

Changing current element name is not possible
   [Documentation]    But start_suite can change test names
   Should be equal    ${SUITE.name}    Pass And Fail
   Check stdout contains    Pass And Fail :: Some tests here
   Check stdout contains    Pass [start suite] ::
   Should be equal   ${SUITE.tests[0].name}    Pass [start suite]

Changing current element docs does not change console output, but does change output.xml
   [Documentation]    But start_suite can change test docs
   Check stdout contains    Pass And Fail :: Some tests here
   Should be equal    ${SUITE.doc}    Some tests here [start suite] [end suite]
   Check stdout contains    Pass [start suite] :: [start suite] ${SPACE*33} | FAIL |
   Check Test Doc    Pass [start suite]    [start suite] [start test] [end test]

Log messages and timestamps can be changed
   ${tc}=   Get test case    Pass [start suite]
   Check log message    ${tc.kws[0].kws[0].msgs[0]}    HELLO SAYS "PASS"!
   Should be equal    ${tc.kws[0].kws[0].msgs[0].timestamp}    20151216 15:51:20.141

Message to syslog can be changed
   Syslog Should Contain Match    20151216 15:51:20.141 | INFO \ | TESTS EXECUTION ENDED. STATISTICS:

File methods and close are called
   Stderr Should Be Equal To    SEPARATOR=\n
   ...    Debug: d.txt
   ...    Output: output.xml
   ...    Xunit: x.xml
   ...    Log: l.html
   ...    Report: r.html
   ...    Close\n
