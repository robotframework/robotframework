*** Settings ***
Suite Setup       Create Input File
Suite Teardown    Remove Temps
Test Setup        Empty Directory    ${MYOUTDIR}
Resource          rebot_resource.robot
Variables         unicode_vars.py

*** Variables ***
${MYOUTDIR}       %{TEMPDIR}${/}robot-test-xunit
${INPUT FILE}     %{TEMPDIR}${/}robot-test-xunit-file.xml
${INVALID}        %{TEMPDIR}${/}ïnvälïd-xünït.xml

*** Test Cases ***
No XUnit Option Given
    Run Rebot    ${EMPTY}    ${INPUT FILE}
    Stderr Should Be Empty
    Stdout Should Not Contain    XUnit

XUnit Option Given
    Run Rebot    --xunit xunit.xml --log log.html    ${INPUT FILE}
    Stderr Should Be Empty
    Stdout Should Contain    XUnit:
    File Should Exist    ${OUTDIR}/xunit.xml
    File Should Exist    ${OUTDIR}/log.html
    Suite Stats Should Be    19    5
    ${root} =    Parse XML    ${OUTDIR}/xunit.xml
    Should Be Equal    ${root.tag}    testsuite
    ${tests} =    Get Elements    ${root}    testcase
    Length Should Be    ${tests}    19
    Element Attribute Should be    ${tests}[7]    name    Ñöñ-ÄŚÇÏÏ Tëśt äņd Këywörd Nämës, Спасибо
    ${failures} =    Get Elements    ${root}    testcase/failure
    Length Should Be    ${failures}    5
    Element Attribute Should be    ${failures}[0]    message    ${MESSAGES}

Times in xUnit output
    Previous Test Should Have Passed    XUnit Option Given
    ${suite} =    Parse XML    ${OUTDIR}/xunit.xml
    Element Attribute Should Match    ${suite}    time    ?.???
    Element Attribute Should Match    ${suite}    time    ?.???    xpath=.//testcase[1]

XUnit skip non-criticals is deprecated
    Run Rebot    --xUnit xunit.xml --xUnitSkipNonCritical     ${INPUT FILE}
    Stderr Should Contain   Command line option --xunitskipnoncritical has been deprecated and has no effect.

Invalid XUnit File
    Create Directory    ${INVALID}
    Run Rebot    -x ${INVALID} -l log.html    ${INPUT FILE}
    File Should Not Exist    ${INVALID}
    File Should Exist    ${OUTDIR}/log.html
    ${path} =    Regexp Escape    ${INVALID}
    Stderr Should Match Regexp
    ...    \\[ ERROR \\] Opening xunit file '${path}' failed: .*

Merge outputs
    Run Rebot    -x xunit.xml    ${INPUT FILE} ${INPUT FILE}
    Suite Stats Should Be     38    10    0    timestamp=${EMPTY}

Start and end time
    Run Rebot    -x xunit.xml --starttime 20211215-12:11:10.456 --endtime 20211215-12:13:10.556    ${INPUT FILE}
    Suite Stats Should Be     19    5    0    120.100    2021-12-15T12:11:10.456000

*** Keywords ***
Create Input File
    Create Output With Robot    ${INPUT FILE}    ${EMPTY}    misc/non_ascii.robot misc/suites
    Create Directory    ${MYOUTDIR}

Remove Temps
    Remove Directory    ${MYOUTDIR}    recursive
    Remove File    ${INPUT FILE}

Suite Stats Should Be
    [Arguments]    ${tests}    ${failures}    ${skipped}=0    ${time}=?.???    ${timestamp}=20??-??-??T??:??:??.???000
    ${suite} =    Get Element    ${OUTDIR}/xunit.xml
    Element Attribute Should Be       ${suite}    tests       ${tests}
    Element Attribute Should Be       ${suite}    failures    ${failures}
    Element Attribute Should Be       ${suite}    skipped     ${skipped}
    Element Attribute Should Be       ${suite}    errors      0
    Element Attribute Should Match    ${suite}    time        ${time}
    Element Attribute Should Match    ${suite}    timestamp   ${timestamp}
