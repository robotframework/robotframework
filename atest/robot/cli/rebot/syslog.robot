*** Settings ***
Suite Teardown    Reset syslog
Test Setup        Reset syslog
Resource          rebot_cli_resource.robot

*** Variables ***
${SYSLOG}         %{TEMPDIR}${/}syslog.txt

*** Test Cases ***
Setting Syslog File
    Set Environment Variable    ROBOT_SYSLOG_FILE    ${SYSLOG}
    Rebot Something
    File Should Not Be Empty    ${SYSLOG}

No syslog
    Rebot Something
    File Should Not Exist    ${SYSLOG}

NONE syslog
    Set Environment Variable    ROBOT_SYSLOG_FILE    NoNe
    Rebot Something
    File Should Not Exist    ${SYSLOG}

Setting Syslog Level
    Set Environment Variable    ROBOT_SYSLOG_FILE    ${SYSLOG}
    Set Environment Variable    ROBOT_SYSLOG_LEVEL    INFO
    Rebot Something
    ${size1} =    Get File Size    ${SYSLOG}
    Set Environment Variable    ROBOT_SYSLOG_LEVEL    DEBUG
    Rebot Something
    ${size2} =    Get File Size    ${SYSLOG}
    Should Be True    0 < ${size1} <= ${size2}
    Set Environment Variable    ROBOT_SYSLOG_LEVEL    warn
    Rebot Something
    File Should Be Empty    ${SYSLOG}

*** Keywords ***
Rebot Something
    ${result} =    Run Rebot Without Processing Output    ${INPUT FILE}
    Should Be Equal    ${result.rc}    ${0}

Reset syslog
    Set Suite Variable    ${SET SYSLOG}    False
    Remove Environment Variable    ROBOT_SYSLOG_FILE
    Remove Environment Variable    ROBOT_SYSLOG_LEVEL
    Remove File    ${SYSLOG}
