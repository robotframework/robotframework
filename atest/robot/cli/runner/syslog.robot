*** Settings ***
Suite Teardown    Reset syslog
Test Setup        Run Keywords    Create Output Directory
...               AND    Reset syslog
Resource          cli_resource.robot

*** Variables ***
${SYSLOG}         %{TEMPDIR}${/}syslog.txt

*** Test Cases ***
No syslog environment variable file
    Run Some Tests
    File Should Not Exist    ${SYSLOG}

Setting syslog sile
    [Documentation]    Also tests that syslog has correct line separators
    Set Environment Variable    ROBOT_SYSLOG_FILE    ${SYSLOG}
    Run Some Tests
    File Should Not Be Empty    ${SYSLOG}
    File Should Have Correct Line Separators    ${SYSLOG}

Syslog file set to NONE
    Set Environment Variable    ROBOT_SYSLOG_FILE    none
    Run Some Tests
    File Should Not Exist    ${SYSLOG}

Invalid syslog file
    Set Environment Variable    ROBOT_SYSLOG_FILE    ${CLI OUTDIR}
    ${result} =    Run Some Tests
    Should Start With    ${result.stderr}    [ ERROR ] Opening syslog file '${CLI OUTDIR}' failed:

Setting syslog Level
    Set Environment Variable    ROBOT_SYSLOG_FILE    ${SYSLOG}
    Set Environment Variable    ROBOT_SYSLOG_LEVEL    INFO
    Run Some Tests
    ${size1} =    Get File Size    ${SYSLOG}
    Set Environment Variable    ROBOT_SYSLOG_LEVEL    DEBUG
    Run Some Tests
    ${size2} =    Get File Size    ${SYSLOG}
    Should Be True    0 < ${size1} < ${size2}
    Set Environment Variable    ROBOT_SYSLOG_LEVEL    warn
    Run Some Tests
    File Should Be Empty    ${SYSLOG}

Invalid syslog level
    Set Environment Variable    ROBOT_SYSLOG_FILE    ${SYSLOG}
    Set Environment Variable    ROBOT_SYSLOG_LEVEL    invalid
    ${result} =    Run Some Tests
    Should Start With    ${result.stderr}    [ ERROR ] Opening syslog file '${SYSLOG}' failed: Invalid log level 'invalid'

*** Keywords ***
Reset syslog
    Set Suite Variable    ${SET SYSLOG}    False
    Remove Environment Variable    ROBOT_SYSLOG_FILE
    Remove Environment Variable    ROBOT_SYSLOG_LEVEL
    Remove File    ${SYSLOG}
