*** Settings ***
Test Setup      Create Output Directory
Suite Teardown  Remove Environment Variable  ROBOT_SYSLOG_FILE
Default Tags    regression  pybot  jybot
Resource        cli_resource.robot


*** Test Cases ***

No syslog environment variable file
    Remove Environment Variable  ROBOT_SYSLOG_FILE
    Run Some Tests
    File Should Not Exist  ${CLI OUTDIR}/syslog.txt

Setting syslog sile
    [Documentation]  Also tests that syslog has correct line separators
    Set Environment Variable  ROBOT_SYSLOG_FILE  ${CLI OUTDIR}${/}syslog.txt
    Run Some Tests
    File Should Not Be Empty  ${CLI OUTDIR}/syslog.txt
    ${syslog} =  Get Binary File  ${CLI OUTDIR}/syslog.txt
    ${linesep} =  Evaluate  os.linesep.encode()  modules=os
    Should Contain  ${syslog}  ${linesep}

Syslog file set to NONE
    Set Environment Variable  ROBOT_SYSLOG_FILE  none
    Run Some Tests
    File Should Not Exist  ${CLI OUTDIR}/syslog.txt

Invalid syslog file
    Set Environment Variable  ROBOT_SYSLOG_FILE  ${CLI OUTDIR}
    ${output} =  Run Some Tests
    Should Start With  ${output}  [ ERROR ] Opening syslog file '${CLI OUTDIR}' failed:

Setting syslog Level
    Set Environment Variable  ROBOT_SYSLOG_FILE  ${CLI OUTDIR}${/}syslog.txt
    Set Environment Variable  ROBOT_SYSLOG_LEVEL  INFO
    Run Some Tests
    ${size1} =  Get File Size  ${CLI OUTDIR}/syslog.txt
    Set Environment Variable  ROBOT_SYSLOG_LEVEL  DEBUG
    Run Some Tests
    ${size2} =  Get File Size  ${CLI OUTDIR}/syslog.txt
    Should Be True  0 < ${size1} < ${size2}
    Set Environment Variable  ROBOT_SYSLOG_LEVEL  warn
    Run Some Tests
    File Should Be Empty  ${CLI OUTDIR}/syslog.txt
    [Teardown]  Remove Environment Variable  ROBOT_SYSLOG_LEVEL

Invalid syslog level
    Set Environment Variable  ROBOT_SYSLOG_LEVEL  invalid
    ${output} =  Run Some Tests
    Should Start With  ${output}  [ ERROR ] Opening syslog file '${CLI OUTDIR}${/}syslog.txt' failed: Invalid log level 'invalid'
    [Teardown]  Remove Environment Variable  ROBOT_SYSLOG_LEVEL
