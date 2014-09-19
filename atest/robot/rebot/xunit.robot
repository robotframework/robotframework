*** Settings ***
Default Tags      regression    jybot    pybot
Suite Setup       Create Input File
Test Setup        Empty Directory     ${MYOUTDIR}
Suite Teardown    Remove Temps
Resource          rebot_resource.robot
Variables         unicode_vars.py

*** Variables ***
${TESTDATA_TEST}    misc${/}unicode.robot
${TESTDATA_SUITES}  misc${/}suites
${MYOUTDIR}         %{TEMPDIR}${/}robot-test-xunit
${INPUT FILE}       %{TEMPDIR}${/}robot-test-xunit-file.xml
${INVALID}          %{TEMPDIR}${/}ïnvälïd-xünït.xml


*** Test Cases ***
No XUnit Option Given
    Run Rebot  ${EMPTY}  ${INPUT FILE}
    Stderr Should Be Empty
    Check Stdout Does Not Contain  XUnit

XUnit Option Given
    Run Rebot  --xunit xunit.xml --log log.html  ${INPUT FILE}
    Stderr Should Be Empty
    Check Stdout Contains  XUnit:
    File Should Exist  ${OUTDIR}/xunit.xml
    File Should Exist  ${OUTDIR}/log.html
    ${root} =  Parse XML  ${OUTDIR}/xunit.xml
    Should Be Equal  ${root.tag}  testsuite
    ${tests} =  Get Elements  ${root}  testcase
    Length Should Be  ${tests}  19
    Should Be Equal  ${tests[7].attrib['name']}  Ünïcödë Tëst änd Këywörd Nämës
    ${failures} =  Get Elements  ${root}  testcase/failure
    Length Should Be  ${failures}  5
    Should Be Equal  ${failures[0].attrib['message']}  ${MESSAGES}

XUnit skip non-criticals
    Run Rebot    --xUnit xunit.xml --xUnitSkipNonCritical --NonCritical f1    ${INPUT FILE}
    Stderr Should Be Empty
    ${root} =    Parse XML  ${OUTDIR}/xunit.xml
    Element Attribute Should Be    ${root}    tests    19
    Element Attribute Should Be    ${root}    failures    4
    Element Attribute Should Be    ${root}    skipped    10
    ${skipped} =  Get Elements  ${root}  xpath=testcase/skipped
    Should Be Equal    ${skipped[0].text}    FAIL: Expected
    Should Be Equal    ${skipped[1].text}    PASS
    Length Should Be    ${skipped}    10

Invalid XUnit File
    Create Directory  ${INVALID}
    Run Rebot  -x ${INVALID} -l log.html  ${INPUT FILE}
    File Should Not Exist  ${INVALID}
    File Should Exist  ${OUTDIR}/log.html
    ${path} =  Regexp Escape  ${INVALID}
    Check Stderr Matches Regexp
    ...  \\[ ERROR \\] Writing xunit file '${path}' failed: .*

--xunitfile is deprecated
    Run Rebot    --xunitfile xunit.xml    ${INPUT FILE}
    Check Stdout Contains  XUnit:
    File Should Exist  ${OUTDIR}/xunit.xml
    Check Stderr Matches Regexp
    ...  \\[ WARN \\] Option --xunitfile is deprecated. Use --xunit instead.

*** Keywords ***
Create Input File
    Create Output With Robot  ${INPUT FILE}  ${EMPTY}  ${TESTDATA_TEST}  ${TESTDATA_SUITES}
    Create Directory  ${MYOUTDIR}

Remove Temps
    Remove Directory  ${MYOUTDIR}  recursive
    Remove File  ${INPUT FILE}
