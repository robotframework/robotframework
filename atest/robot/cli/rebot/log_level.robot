*** Settings ***
Resource          rebot_cli_resource.robot

*** Variables ***
${LOG NAME}       logfile.html

*** Test Cases ***
By default all messages are included
    ${tc} =    Rebot
    Check Log Message    ${tc[0, 0]}    Arguments: [ 'Test 1' ]    TRACE
    Check Log Message    ${tc[0, 1]}    Test 1    INFO
    Check Log Message    ${tc[0, 2]}    Return: None    TRACE
    Check Log Message    ${tc[1, 0]}    Arguments: [ 'Logging with debug level' | 'DEBUG' ]    TRACE
    Check Log Message    ${tc[1, 1]}    Logging with debug level    DEBUG
    Check Log Message    ${tc[1, 2]}    Return: None    TRACE
    Min level should be 'TRACE' and default 'TRACE'

Levels below given level are ignored
    ${tc} =    Rebot    --loglevel debug
    Check Log Message    ${tc[0, 0]}    Test 1    INFO
    Check Log Message    ${tc[1, 0]}    Logging with debug level    DEBUG
    Min level should be 'DEBUG' and default 'DEBUG'
    ${tc} =    Rebot    -L INFO
    Check Log Message    ${tc[0, 0]}    Test 1    INFO
    Should Be Empty      ${tc[1].body}
    Should Be Empty      ${tc[2, 0].body}
    Min level should be 'INFO' and default 'INFO'

All messages are ignored when NONE level is used
    ${tc} =    Rebot    --loglevel NONE
    Should Be Empty    ${tc[0].body}
    Should Be Empty    ${tc[1].body}
    Min level should be 'NONE' and default 'NONE'

Configure visible log level
    Rebot    --LogLevel DEBUG:INFO
    Min level should be 'DEBUG' and default 'INFO'

*** Keywords ***
Rebot
    [Arguments]    ${options}=${EMPTY}
    Run Rebot    ${options} --log ${LOGNAME}    ${INPUT FILE}
    RETURN    ${SUITE.tests[0]}

Min level should be '${min}' and default '${default}'
    ${log}=    Get file    ${OUTDIR}/${LOG NAME}
    Should contain    ${log}    "minLevel":"${min}"
    Should contain    ${log}    "defaultLevel":"${default}"
