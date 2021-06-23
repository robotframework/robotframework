*** Settings ***
Resource        atest_resource.robot

*** Variables ***
${REBOT INFILE}    %{TEMPDIR}/robot-rebot-infile.xml

*** Test Cases ***

Outputs generated at runtime should have correct line separators
    Run Tests    -l log -r report -x xunit -b debug -L DEBUG    misc/pass_and_fail.robot
    Outputs Should Have Correct Line Separators
    ...    output.xml    log.html    report.html    xunit.xml    debug.txt

Split logs generated at runtime should have correct line separators
    Run Tests    -l log --splitlog -L DEBUG    misc/pass_and_fail.robot
    Outputs Should Have Correct Line Separators
    ...    output.xml    log.html    log-1.js    log-2.js    log-3.js

Outputs generated with rebot should have correct line separators
    Copy File    ${OUTFILE}    ${REBOT INFILE}
    Run Rebot    -l log -r report -x xunit -L DEBUG    ${REBOT INFILE}
    Outputs Should Have Correct Line Separators
    ...    output.xml    log.html    report.html    xunit.xml
    [Teardown]    Remove File    ${REBOT INFILE}

*** Keywords ***

Outputs Should Have Correct Line Separators
    [Arguments]    @{outputs}
    FOR    ${name}    IN    @{outputs}  ${SYSLOG FILE}
        ${path} =    Join Path    ${OUTDIR}    ${name}
        File Should Have Correct Line Separators    ${path}
    END
