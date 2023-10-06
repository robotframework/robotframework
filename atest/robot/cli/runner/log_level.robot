*** Settings ***
Documentation   Tests for setting log level from command line with --loglevel option. Setting log level while executing tests (BuiltIn.Set Log Level) is tested with BuiltIn library keywords.
Resource        atest_resource.robot

*** Variables ***
${TESTDATA}  misc/pass_and_fail.robot
${LOG NAME}   logfile.html

*** Test Cases ***
No Log Level Given
    [Documentation]    Default level of INFO should be used
    Run Tests    ${EMPTY}    ${TESTDATA}
    Check Log Message    ${SUITE.tests[0].kws[0].kws[0].msgs[0]}    Hello says "Pass"!    INFO
    Should Be Empty      ${SUITE.tests[0].kws[0].kws[1].messages}
    Check Log Message    ${SUITE.tests[1].kws[1].msgs[0]}           Expected failure      FAIL

Trace Level
    Run Tests  --loglevel TRACE  ${TESTDATA}
    Should Log On Trace Level

Debug Level
    Run Tests  --loglevel debug --log ${LOG NAME}  ${TESTDATA}
    Should Log On Debug Level
    Min level should be 'DEBUG' and default 'DEBUG'

Debug Level With Default Info
    Run Tests  --loglevel dEBug:iNfo --log ${LOG NAME}  ${TESTDATA}
    Should Log On Debug Level
    Min level should be 'DEBUG' and default 'INFO'

Trace Level With Default Debug
    Run Tests  --loglevel trace:Debug --log ${LOG NAME}  ${TESTDATA}
    Should Log On Trace Level
    Min level should be 'TRACE' and default 'DEBUG'

Info Level
    Run Tests    -L InFo    ${TESTDATA}
    Check Log Message    ${SUITE.tests[0].kws[0].kws[0].msgs[0]}    Hello says "Pass"!    INFO
    Should Be Empty      ${SUITE.tests[0].kws[0].kws[1].messages}
    Check Log Message    ${SUITE.tests[1].kws[1].msgs[0]}           Expected failure      FAIL

Warn Level
    Run Tests    --loglevel WARN --variable LEVEL1:WARN --variable LEVEL2:INFO    ${TESTDATA}
    Check Log Message    ${SUITE.tests[0].kws[0].kws[0].msgs[0]}    Hello says "Pass"!    WARN
    Should Be Empty      ${SUITE.tests[0].kws[0].kws[1].messages}
    Check Log Message    ${SUITE.tests[1].kws[1].msgs[0]}           Expected failure      FAIL

Warnings Should Be Written To Syslog
    Should Be Equal  ${PREV TEST NAME}  Warn Level
    Check Log Message  ${ERRORS.msgs[0]}  Hello says "Suite Setup"!  WARN
    Check Log Message  ${ERRORS.msgs[1]}  Hello says "Pass"!  WARN
    Check Log Message  ${ERRORS.msgs[2]}  Hello says "Fail"!  WARN
    Length Should Be  ${ERRORS.msgs}    3
    Syslog Should Contain  | WARN \ |  Hello says "Suite Setup"!
    Syslog Should Contain  | WARN \ |  Hello says "Pass"!
    Syslog Should Contain  | WARN \ |  Hello says "Fail"!

Error Level
    Run Tests    --loglevel ERROR --variable LEVEL1:ERROR --variable LEVEL2:WARN    ${TESTDATA}
    Check Log Message    ${SUITE.tests[0].kws[0].kws[0].msgs[0]}    Hello says "Pass"!    ERROR
    Should Be Empty      ${SUITE.tests[0].kws[0].kws[1].messages}
    Check Log Message    ${SUITE.tests[1].kws[1].msgs[0]}           Expected failure      FAIL

None Level
    Run Tests    --loglevel NONE --log ${LOG NAME} --variable LEVEL1:ERROR --variable LEVEL2:WARN    ${TESTDATA}
    Should Be Empty    ${SUITE.tests[0].kws[0].kws[0].messages}
    Should Be Empty    ${SUITE.tests[0].kws[0].kws[1].messages}
    Should Be Empty    ${SUITE.tests[1].kws[1].messages}
    Min level should be 'NONE' and default 'NONE'

*** Keywords ***
Min level should be '${min}' and default '${default}'
    ${log}=    Get file      ${OUTDIR}/${LOG NAME}
    Should contain    ${log}    "minLevel":"${min}"
    Should contain    ${log}    "defaultLevel":"${default}"

Should Log On Debug Level
    Check Log Message  ${SUITE.tests[0].kws[0].kws[0].msgs[0]}  Hello says "Pass"!  INFO
    Check Log Message  ${SUITE.tests[0].kws[0].kws[1].msgs[0]}  Debug message  DEBUG
    Check Log Message  ${SUITE.tests[1].kws[1].msgs[0]}  Expected failure  FAIL

Should Log On Trace Level
    Check Log Message  ${SUITE.tests[0].kws[0].kws[0].msgs[0]}  Arguments: [ 'Hello says "Pass"!' | 'INFO' ]  TRACE
    Check Log Message  ${SUITE.tests[0].kws[0].kws[0].msgs[1]}  Hello says "Pass"!  INFO
    Check Log Message  ${SUITE.tests[0].kws[0].kws[0].msgs[2]}  Return: None  TRACE
    Check Log Message  ${SUITE.tests[0].kws[0].kws[1].msgs[1]}  Debug message  DEBUG
    Check Log Message  ${SUITE.tests[1].kws[1].msgs[0]}  Arguments: [ 'Expected failure' ]  TRACE
    Check Log Message  ${SUITE.tests[1].kws[1].msgs[1]}  Expected failure  FAIL
