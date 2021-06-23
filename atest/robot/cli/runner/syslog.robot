*** Settings ***
Test Setup              Run Keywords
...                     Create Output Directory    AND
...                     Reset syslog
Suite Teardown          Reset syslog
Resource                cli_resource.robot

*** Variables ***
${SYSLOG}               %{TEMPDIR}${/}syslog.txt
${SYSLOG IN EXECDIR}    ${INTERPRETER.output_name}-syslog.txt
${SYSLOG IN NEW DIR}    %{TEMPDIR}/new-dir-and/also-unix-separator-always/with/sys.log

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

Syslog as name only
    Set Environment Variable    ROBOT_SYSLOG_FILE    ${SYSLOG IN EXECDIR}
    Run Some Tests
    File Should Not Be Empty    ${EXECDIR}/${SYSLOG IN EXECDIR}
    File Should Have Correct Line Separators    ${EXECDIR}/${SYSLOG IN EXECDIR}

Syslog directory is automatically created
    Set Environment Variable    ROBOT_SYSLOG_FILE    ${SYSLOG IN NEW DIR}
    Run Some Tests
    File Should Not Be Empty    ${SYSLOG IN NEW DIR}
    File Should Have Correct Line Separators    ${SYSLOG IN NEW DIR}

Syslog file set to NONE
    Set Environment Variable    ROBOT_SYSLOG_FILE    none
    Run Some Tests
    File Should Not Exist    ${SYSLOG}
    File Should Not Exist    ${SYSLOG IN EXECDIR}
    File Should Not Exist    ${SYSLOG IN NEW DIR}

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
    Remove Files    ${SYSLOG}    ${EXECDIR}/${SYSLOG IN EXECDIR}
    ${syslog dir}    ${_} =    Split Path    ${SYSLOG IN NEW DIR}
    Remove Directory    ${syslog dir}    recursive=True
