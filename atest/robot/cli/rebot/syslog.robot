*** Settings ***
Test Setup      Empty Directory  ${MYOUTDIR}
Force Tags      regression
Resource        atest_resource.robot
Resource        rebot_cli_resource.robot

*** Test Cases ***
Setting Syslog File
    Set Environment Variable  ROBOT_SYSLOG_FILE  ${MYOUTDIR}${/}syslog.txt
    Rebot Something
    File Should Not Be Empty  ${MYOUTDIR}${/}syslog.txt
    Remove File  ${MYOUTDIR}${/}syslog.txt
    Remove Environment Variable  ROBOT_SYSLOG_FILE
    Log Environment Variables
    Rebot Something
    File Should Not Exist  ${MYOUTDIR}${/}syslog.txt
    Set Environment Variable  ROBOT_SYSLOG_FILE  none
    Rebot Something
    File Should Not Exist  ${MYOUTDIR}${/}syslog.txt
    [Teardown]  Remove syslog environment variables

Setting Syslog Level
    Set Environment Variable  ROBOT_SYSLOG_FILE  ${MYOUTDIR}${/}syslog.txt
    Set Environment Variable  ROBOT_SYSLOG_LEVEL  INFO
    Rebot Something
    ${size1} =  Get File Size  ${MYOUTDIR}${/}syslog.txt
    Set Environment Variable  ROBOT_SYSLOG_LEVEL  DEBUG
    Rebot Something
    ${size2} =  Get File Size  ${MYOUTDIR}${/}syslog.txt
    Should Be True  0 < ${size1} <= ${size2}
    Set Environment Variable  ROBOT_SYSLOG_LEVEL  warn
    Rebot Something
    File Should Be Empty  ${MYOUTDIR}${/}syslog.txt
    [Teardown]  Remove syslog environment variables

*** Keywords ***
Remove syslog environment variables
    Remove Environment Variable  ROBOT_SYSLOG_FILE
    Remove Environment Variable  ROBOT_SYSLOG_LEVEL

Rebot Something
    Run  ${REBOT} --outputdir ${MYOUTDIR} ${MYINPUT}
