*** Settings ***
Suite Setup       Create Input Files
Suite Teardown    Remove Files    ${INPUT1}    ${INPUT2}
Resource          rebot_resource.robot

*** Variables ***
${INPUT1}         %{TEMPDIR}${/}rebot-test-a.xml
${INPUT2}         %{TEMPDIR}${/}rebot-test-b.xml
${COMBINED}       %{TEMPDIR}${/}combined.xml

*** Test Cases ***
Combine With Both Starttime and endtime should Set Correct Elapsed Time
    Log Many    ${INPUT1}    ${INPUT2}
    Run Rebot    --starttime 2007:09:25:21:51 --endtime 2007:09:26:01:12:30.200    ${INPUT1} ${INPUT2}
    Should Be Equal    ${SUITE.starttime}    20070925 21:51:00.000
    Should Be Equal    ${SUITE.endtime}    20070926 01:12:30.200
    Should Be True    ${SUITE.elapsedtime} == (3*60*60 + 21*60 + 30) * 1000 + 200

Combine With Only Starttime Should Only Affect Starttime
    Run Rebot    --starttime 20070925-2151    ${INPUT1} ${INPUT2}
    Should Be Equal    ${SUITE.starttime}    20070925 21:51:00.000
    Should Be Equal    ${SUITE.endtime}    ${ORIG_END}
    Should Be Equal    ${SUITE.elapsedtime}    ${ORIG_ELAPSED}

Combine With Only Endtime Should Only Affect Endtime
    Run Rebot    --endtime 2010_01.01:12-33    ${INPUT1} ${INPUT2}
    Should Be Equal    ${SUITE.starttime}    ${ORIG_START}
    Should Be Equal    ${SUITE.endtime}    20100101 12:33:00.000
    Should Be Equal    ${SUITE.elapsedtime}    ${ORIG_ELAPSED}

Recombining Should Work
    ${options} =    Catenate
    ...    --starttime 2007:09:25:21:51
    ...    --endtime 2007:09:26:01:12:30:200
    ...    --output ${COMBINED}
    Run Rebot Without Processing Output    ${options}    ${INPUT1} ${INPUT2}
    Run Rebot    ${EMPTY}    ${INPUT1} ${INPUT2} ${COMBINED}
    Should Be True    '${SUITE.elapsedtime}' > '03:21:30.200'

It should Be possible to Omit Time Altogether
    Run Rebot    --starttime 2007-10-01 --endtime 20071006    ${INPUT1} ${INPUT2}
    Should Be Equal    ${SUITE.starttime}    20071001 00:00:00.000
    Should Be Equal    ${SUITE.endtime}    20071006 00:00:00.000
    Should Be True    ${SUITE.elapsedtime} == 120*60*60 * 1000

Use Starttime With Single Output
    Run Rebot    --starttime 20070925-2151    ${INPUT1}
    Should Be Equal    ${SUITE.starttime}    20070925 21:51:00.000
    Should Be Equal    ${SUITE.endtime}    ${SINGLE_SUITE_ORIG_END}
    Should Be True    ${SUITE.elapsedtime} > ${SINGLE SUITE ORIG ELAPSED}

Use Endtime With Single Output
    Run Rebot    --endtime 20070925-2151    ${INPUT1}
    Should Be Equal    ${SUITE.starttime}    ${SINGLE_SUITE_ORIG_START}
    Should Be Equal    ${SUITE.endtime}    20070925 21:51:00.000
    Should Be True    ${SUITE.elapsedtime} < ${SINGLE SUITE ORIG ELAPSED}

Use Starttime And Endtime With Single Output
    Run Rebot    --starttime 20070925-2151 --endtime 20070925-2252    ${INPUT1}
    Should Be Equal    ${SUITE.starttime}    20070925 21:51:00.000
    Should Be Equal    ${SUITE.endtime}    20070925 22:52:00.000
    Should Be Equal    ${SUITE.elapsedtime}    ${3660000}

*** Keywords ***
Create Input Files
    Create Output With Robot    ${INPUT1}    ${EMPTY}    misc/normal.robot
    Create Output With Robot    ${INPUT2}    ${EMPTY}    misc/suites/tsuite1.robot
    Run Rebot    ${EMPTY}    ${INPUT1} ${INPUT2}
    Set Suite Variable    $ORIG_START    ${SUITE.starttime}
    Set Suite Variable    $ORIG_END    ${SUITE.endtime}
    Set Suite Variable    $ORIG_ELAPSED    ${SUITE.elapsedtime}
    Run Rebot    ${EMPTY}    ${INPUT1}
    Set Suite Variable    $SINGLE_SUITE_ORIG_START    ${SUITE.starttime}
    Set Suite Variable    $SINGLE_SUITE_ORIG_END    ${SUITE.endtime}
    Set Suite Variable    $SINGLE_SUITE_ORIG_ELAPSED    ${SUITE.elapsedtime}
