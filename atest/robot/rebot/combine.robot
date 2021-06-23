*** Settings ***
Suite Setup       Create Inputs For Rebot
Suite Teardown    Remove Temp Files
Resource          rebot_resource.robot

*** Variables ***
${TEMP OUT 1}     %{TEMPDIR}${/}rebot-test-1.xml
${TEMP OUT 2}     %{TEMPDIR}${/}rebot-test-2.xml
${COMB OUT 1}     %{TEMPDIR}${/}rebot-test-3.xml
${COMB OUT 2}     %{TEMPDIR}${/}rebot-test-4.xml
${COMB OUT 3}     %{TEMPDIR}${/}rebot-test-5.xml
${COMB OUT 4}     %{TEMPDIR}${/}rebot-test-6.xml
${OUT PATTERN}    %{TEMPDIR}${/}rebot-test-?.*
${SUITE1}         Set in suite setup by combining Pass And Fail and Normal w/o options.
${SUITE2}         As previous but with --name, --doc, etc.
${SUITE3}         Combined from Pass And Fail, Normal and Times
${SUITE4}         Combined from SUITE2 (recombine) and Times
@{PASS FAIL}      Pass         Fail
@{NORMAL}         First One    Second One
@{TIMES}          Incl-1       Incl-12    Incl-123    Excl-1    Excl-12    Excl-123

*** Test Cases ***
Combining Two
    Should Contain Suites    ${SUITE1}    Pass And Fail    Normal
    Should Contain Suites    ${SUITE2}    Pass And Fail    Normal
    Should Contain Tests    ${SUITE1}    @{PASS FAIL}    @{NORMAL}
    Should Contain Tests    ${SUITE1.suites[0]}    @{PASS FAIL}
    Should Contain Tests    ${SUITE1.suites[1]}    @{NORMAL}
    Should Contain Tests    ${SUITE2}    @{PASS FAIL}    @{NORMAL}
    Should Contain Tests    ${SUITE2.suites[0]}    @{PASS FAIL}
    Should Contain Tests    ${SUITE2.suites[1]}    @{NORMAL}

Combining Three
    Should Contain Suites    ${SUITE3}    Pass And Fail    Normal    Times
    Should Contain Tests    ${SUITE3}    @{PASS FAIL}    @{NORMAL}    @{TIMES}
    Should Contain Tests    ${SUITE3.suites[0]}    @{PASS FAIL}
    Should Contain Tests    ${SUITE3.suites[1]}    @{NORMAL}
    Should Contain Tests    ${SUITE3.suites[2]}    @{TIMES}

Recombining
    Should Contain Suites    ${SUITE4}    Times    New Name
    Should Contain Suites    ${SUITE4.suites[1]}    Pass And Fail    Normal
    Should Contain Tests    ${SUITE4}    @{TIMES}    @{PASS FAIL}    @{NORMAL}
    Should Contain Tests    ${SUITE4.suites[0]}    @{TIMES}
    Should Contain Tests    ${SUITE4.suites[1]}    @{PASS FAIL}    @{NORMAL}
    Should Contain Tests    ${SUITE4.suites[1].suites[0]}    @{PASS FAIL}
    Should Contain Tests    ${SUITE4.suites[1].suites[1]}    @{NORMAL}

Default Suite Name When Combining Two
    Check Names    ${SUITE1}    Pass And Fail & Normal
    Check Names    ${SUITE1.suites[0]}    Pass And Fail    Pass And Fail & Normal.
    Check Names    ${SUITE1.suites[1]}    Normal    Pass And Fail & Normal.

Overridden Suite Name
    Check Names    ${SUITE2}    New Name
    Check Names    ${SUITE2.suites[0]}    Pass And Fail    New Name.
    Check Names    ${SUITE2.suites[1]}    Normal    New Name.

Default Suite Name When Combining Three
    Check Names    ${SUITE3}    Pass And Fail & Normal & Times
    Check Names    ${SUITE3.suites[0]}    Pass And Fail    Pass And Fail & Normal & Times.
    Check Names    ${SUITE3.suites[1]}    Normal    Pass And Fail & Normal & Times.
    Check Names    ${SUITE3.suites[2]}    Times    Pass And Fail & Normal & Times.

Default Suite Name When Recombining
    Check Names    ${SUITE4}    Times & New Name
    Check Names    ${SUITE4.suites[0]}    Times    Times & New Name.
    Check Names    ${SUITE4.suites[1]}    New Name    Times & New Name.
    Check Names    ${SUITE4.suites[1].suites[0]}    Pass And Fail    Times & New Name.New Name.
    Check Names    ${SUITE4.suites[1].suites[1]}    Normal    Times & New Name.New Name.

Suite Documemtation
    Should Be Equal    ${SUITE1.doc}    ${EMPTY}
    Should Be Equal    ${SUITE2.doc}    My fine doc
    Should Be Equal    ${SUITE4.doc}    ${EMPTY}
    Should Be Equal    ${SUITE4.suites[1].doc}    My fine doc

Suite Metadata
    Should Be True    ${SUITE1.metadata} == {}
    Should Be Equal    ${SUITE2.metadata['Name']}    value
    Should Be Equal    ${SUITE2.metadata['Other Meta']}    Another value

Suite Times
    Should Be Equal    ${SUITE3.starttime}    ${NONE}
    Should Be Equal    ${SUITE3.endtime}    ${NONE}
    Elapsed Time Should Be Valid    ${SUITE3.elapsedtime}
    Should Be True    ${SUITE3.elapsedtime} == ${MILLIS1} + ${MILLIS2} + 9999
    Timestamp Should Be Valid    ${SUITE3.suites[0].starttime}
    Timestamp Should Be Valid    ${SUITE3.suites[0].endtime}
    Elapsed Time Should Be Valid    ${SUITE3.suites[0].elapsedtime}
    Should Be Equal    ${SUITE3.suites[0].elapsedtime}    ${MILLIS1}
    Timestamp Should Be Valid    ${SUITE3.suites[1].starttime}
    Timestamp Should Be Valid    ${SUITE3.suites[1].endtime}
    Elapsed Time Should Be Valid    ${SUITE3.suites[1].elapsedtime}
    Should Be Equal    ${SUITE3.suites[1].elapsedtime}    ${MILLIS2}
    Should Be Equal    ${SUITE3.suites[2].starttime}    20061227 11:59:59.000
    Should Be Equal    ${SUITE3.suites[2].endtime}    20061227 12:00:08.999
    Should Be Equal    ${SUITE3.suites[2].elapsedtime}    ${9999}

Suite Times In Recombine
    Should Be Equal    ${SUITE4.starttime}    ${NONE}
    Should Be Equal    ${SUITE4.endtime}    ${NONE}
    Should Be True    ${SUITE4.elapsedtime} == 9999 + ${MILLIS1} + ${MILLIS2}
    Should Be Equal    ${SUITE4.suites[0].starttime}    20061227 11:59:59.000
    Should Be Equal    ${SUITE4.suites[0].endtime}    20061227 12:00:08.999
    Should Be Equal    ${SUITE4.suites[0].elapsedtime}    ${9999}
    Should Be Equal    ${SUITE4.suites[1].starttime}    ${NONE}
    Should Be Equal    ${SUITE4.suites[1].endtime}    ${NONE}
    Timestamp Should Be Valid    ${SUITE4.suites[1].suites[0].starttime}
    Timestamp Should Be Valid    ${SUITE4.suites[1].suites[0].endtime}
    Elapsed Time Should Be Valid    ${SUITE4.suites[1].suites[0].elapsedtime}
    Should Be Equal    ${SUITE4.suites[1].suites[0].elapsedtime}    ${MILLIS1}
    Timestamp Should Be Valid    ${SUITE4.suites[1].suites[1].starttime}
    Timestamp Should Be Valid    ${SUITE4.suites[1].suites[1].endtime}
    Elapsed Time Should Be Valid    ${SUITE4.suites[1].suites[1].elapsedtime}
    Should Be Equal    ${SUITE4.suites[1].suites[1].elapsedtime}    ${MILLIS2}

Elapsed Time Should Be Written To Output When Start And End Time Are Not Known
    ${combined} =    Get Element    ${COMB OUT 1}    suite/status
    Element Attribute Should Be    ${combined}    starttime    N/A
    Element Attribute Should Be    ${combined}    endtime    N/A
    Should Be True    int($combined.get('elapsedtime')) >= 0
    ${originals} =    Get Elements    ${COMB OUT 1}    suite/suite/status
    Element Attribute Should Match    ${originals[0]}    starttime    20?????? ??:??:??.???
    Element Attribute Should Match    ${originals[0]}    endtime    20?????? ??:??:??.???
    Element Should Not Have Attribute    ${originals[0]}    elapsedtime

Combined Suite Names Are Correct In Statistics
    ${suites} =    Get Suite Stat Nodes    ${COMB OUT 1}
    Should Be Equal    ${suites[0].text}    Pass And Fail & Normal
    Should Be Equal    ${suites[1].text}    Pass And Fail & Normal.Pass And Fail
    Should Be Equal    ${suites[2].text}    Pass And Fail & Normal.Normal
    ${suites} =    Get Suite Stat Nodes    ${COMB OUT 2}
    Should Be Equal    ${suites[0].text}    New Name
    Should Be Equal    ${suites[1].text}    New Name.Pass And Fail
    Should Be Equal    ${suites[2].text}    New Name.Normal

Wildcards
    Run Rebot    ${EMPTY}    ${OUT PATTERN}
    Should Contain Suites    ${SUITE}    Pass And Fail    Normal    Pass And Fail & Normal
    ...    New Name    Pass And Fail & Normal & Times    Times & New Name

*** Keywords ***
Create inputs for Rebot
    Create first input for Rebot
    Create second input for Rebot
    Combine without options
    Combine with options
    Combine with output with known times
    Recombine
    Prevent accidental usage of ${SUITE} variable

Create first input for Rebot
    Create Output With Robot    ${TEMP OUT 1}    ${EMPTY}    misc/pass_and_fail.robot
    Set Suite Variable    $MILLIS1    ${ORIG ELAPSED}

Create second input for Rebot
    Create Output With Robot    ${TEMP OUT 2}    ${EMPTY}    misc/normal.robot
    Set Suite Variable    $MILLIS2    ${ORIG ELAPSED}

Combine without options
    Run Rebot    ${EMPTY}    ${TEMP OUT 1} ${TEMP OUT 2}
    Set Suite Variable    $SUITE1    ${SUITE}
    Copy File    ${OUT FILE}    ${COMB OUT 1}

Combine with options
    ${options} =    Catenate
    ...    --name "New Name"
    ...    --doc "My fine doc"
    ...    --metadata Name:value
    ...    -M "Other Meta:Another value"
    Run Rebot    ${options}    ${TEMP OUT 1} ${TEMP OUT 2}
    Set Suite Variable    $SUITE2    ${SUITE}
    Copy File    ${OUT FILE}    ${COMB OUT 2}

Combine with output with known times
    Run Rebot    ${EMPTY}    ${TEMP OUT 1} ${TEMP OUT 2} rebot/times.xml
    Copy File    ${OUT FILE}    ${COMB OUT 3}
    Set Suite Variable    $SUITE3    ${SUITE}

Recombine
    Run Rebot    ${EMPTY}    rebot/times.xml ${COMB OUT 2}
    Set Suite Variable    $SUITE4    ${SUITE}
    Copy File    ${OUT FILE}    ${COMB OUT 4}

Prevent accidental usage of ${SUITE} variable
    Set Suite Variable    $SUITE    ${None}

Remove Temp Files
    Remove Files    ${OUT PATTERN}
