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

*** Keywords ***
Create Input File
    Create Output With Robot    ${INPUT FILE}    ${EMPTY}    misc/non_ascii.robot misc/suites
    Create Directory    ${MYOUTDIR}

Remove Temps
    Remove Directory    ${MYOUTDIR}    recursive
    Remove File    ${INPUT FILE}
