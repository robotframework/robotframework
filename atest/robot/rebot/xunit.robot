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
    ${suites} =    Get Elements    ${root}    testsuite
    Length Should Be    ${suites}    2
    ${tests} =    Get Elements    ${suites}[0]    testcase
    Length Should Be    ${tests}    8
    Element Attribute Should be    ${tests}[7]    name    Ñöñ-ÄŚÇÏÏ Tëśt äņd Këywörd Nämës, Спасибо
    ${failures} =    Get Elements    ${suites}[0]    testcase/failure
    Length Should Be    ${failures}    4
    Element Attribute Should be    ${failures}[0]    message    ${MESSAGES}
    ${properties} =    Get Elements    ${suites}[1]    testsuite[6]/properties/property
    Length Should Be    ${properties}    2
    Element Attribute Should be    ${properties}[0]    name     Documentation
    Element Attribute Should be    ${properties}[0]    value    Normal test cases

Suite Stats
    [Template]    Suite Stats Should Be
    21    5
    8     4    xpath=testsuite[1]
    13    1    xpath=testsuite[2]
    1     1    xpath=testsuite[2]/testsuite[2]
    2     0    xpath=testsuite[2]/testsuite[3]
    1     0    xpath=testsuite[2]/testsuite[3]/testsuite[1]
    1     0    xpath=testsuite[2]/testsuite[3]/testsuite[2]
    3     0    xpath=testsuite[2]/testsuite[4]
    1     0    xpath=testsuite[2]/testsuite[4]/testsuite[1]
    2     0    xpath=testsuite[2]/testsuite[4]/testsuite[2]
    3     0    xpath=testsuite[2]/testsuite[6]
    1     0    xpath=testsuite[2]/testsuite[7]
    1     0    xpath=testsuite[2]/testsuite[8]

Times in xUnit output
    Previous Test Should Have Passed    Suite Stats
    ${suite} =    Parse XML    ${OUTDIR}/xunit.xml
    Element Attribute Should Match    ${suite}    time    ?.???
    Element Attribute Should Match    ${suite}    time    ?.???    xpath=testsuite[1]
    Element Attribute Should Match    ${suite}    time    ?.???    xpath=testsuite[1]/testcase[2]
    Element Attribute Should Match    ${suite}    time    ?.???    xpath=testsuite[2]/testsuite[2]/testcase[1]

Suite Properties
    [Template]    Suite Properties Should Be
    0
    0     xpath=testsuite[1]
    0     xpath=testsuite[2]
    2     xpath=testsuite[2]/testsuite[2]
    0     xpath=testsuite[2]/testsuite[3]
    2     xpath=testsuite[2]/testsuite[3]/testsuite[1]
    2     xpath=testsuite[2]/testsuite[3]/testsuite[2]
    0     xpath=testsuite[2]/testsuite[4]
    0     xpath=testsuite[2]/testsuite[4]/testsuite[1]
    2     xpath=testsuite[2]/testsuite[4]/testsuite[2]
    2     xpath=testsuite[2]/testsuite[6]
    2     xpath=testsuite[2]/testsuite[7]
    2     xpath=testsuite[2]/testsuite[8]

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
    Suite Stats Should Be     42    10    0    timestamp=${EMPTY}

Merged Suite properties
    [Template]    Suite Properties Should Be
    0
    0     xpath=testsuite[1]
    0     xpath=testsuite[1]/testsuite[1]
    0     xpath=testsuite[1]/testsuite[2]
    2     xpath=testsuite[1]/testsuite[2]/testsuite[2]
    0     xpath=testsuite[1]/testsuite[2]/testsuite[3]
    2     xpath=testsuite[1]/testsuite[2]/testsuite[3]/testsuite[1]
    2     xpath=testsuite[1]/testsuite[2]/testsuite[3]/testsuite[2]
    0     xpath=testsuite[1]/testsuite[2]/testsuite[4]
    0     xpath=testsuite[1]/testsuite[2]/testsuite[4]/testsuite[1]
    2     xpath=testsuite[1]/testsuite[2]/testsuite[4]/testsuite[2]
    2     xpath=testsuite[1]/testsuite[2]/testsuite[6]
    2     xpath=testsuite[1]/testsuite[2]/testsuite[7]
    2     xpath=testsuite[1]/testsuite[2]/testsuite[8]
    0     xpath=testsuite[2]
    0     xpath=testsuite[2]/testsuite[1]
    0     xpath=testsuite[2]/testsuite[2]
    2     xpath=testsuite[2]/testsuite[2]/testsuite[2]
    0     xpath=testsuite[2]/testsuite[2]/testsuite[3]
    2     xpath=testsuite[2]/testsuite[2]/testsuite[3]/testsuite[1]
    2     xpath=testsuite[2]/testsuite[2]/testsuite[3]/testsuite[2]
    0     xpath=testsuite[2]/testsuite[2]/testsuite[4]
    0     xpath=testsuite[2]/testsuite[2]/testsuite[4]/testsuite[1]
    2     xpath=testsuite[2]/testsuite[2]/testsuite[4]/testsuite[2]
    2     xpath=testsuite[2]/testsuite[2]/testsuite[6]
    2     xpath=testsuite[2]/testsuite[2]/testsuite[7]
    2     xpath=testsuite[2]/testsuite[2]/testsuite[8]

Start and end time
    Run Rebot    -x xunit.xml --starttime 20211215-12:11:10.456 --endtime 20211215-12:13:10.556    ${INPUT FILE}
    Suite Stats Should Be     21    5    0    120.100    2021-12-15T12:11:10.456000

*** Keywords ***
Create Input File
    Create Output With Robot    ${INPUT FILE}    ${EMPTY}    misc/non_ascii.robot misc/suites
    Create Directory    ${MYOUTDIR}

Remove Temps
    Remove Directory    ${MYOUTDIR}    recursive
    Remove File    ${INPUT FILE}

Suite Stats Should Be
    [Arguments]    ${tests}    ${failures}    ${skipped}=0
    ...    ${time}=?.???    ${timestamp}=20??-??-??T??:??:??.??????
    ...    ${xpath}=.
    ${suite} =    Get Element    ${OUTDIR}/xunit.xml    xpath=${xpath}
    Element Attribute Should Be       ${suite}    tests       ${tests}
    Element Attribute Should Be       ${suite}    failures    ${failures}
    Element Attribute Should Be       ${suite}    skipped     ${skipped}
    Element Attribute Should Be       ${suite}    errors      0
    Element Attribute Should Match    ${suite}    time        ${time}
    Element Attribute Should Match    ${suite}    timestamp   ${timestamp}

Suite Properties Should Be
    [Arguments]    ${property_count}    ${xpath}=.
    ${suite} =    Get Element    ${OUTDIR}/xunit.xml    xpath=${xpath}
    ${properties_element} =    Get Elements    ${suite}    properties
    IF    ${property_count}
        Length Should Be    ${properties_element}    1
        ${property_elements} =    Get Elements    ${properties_element}[0]    property
        Length Should Be    ${property_elements}    ${property_count}
    ELSE
        Length Should Be    ${properties_element}    0
    END
