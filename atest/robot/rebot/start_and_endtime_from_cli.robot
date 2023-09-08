*** Settings ***
Suite Setup       Create Input Files
Suite Teardown    Remove Files    ${INPUT1}    ${INPUT2}
Resource          rebot_resource.robot

*** Variables ***
${INPUT1}         %{TEMPDIR}${/}rebot-test-a.xml
${INPUT2}         %{TEMPDIR}${/}rebot-test-b.xml
${COMBINED}       %{TEMPDIR}${/}combined.xml

*** Test Cases ***
Combine with both start time and end time
    Log Many    ${INPUT1}    ${INPUT2}
    Run Rebot    --starttime 2007:09:25:21:51 --endtime 2007-09-26T01:12:30.200    ${INPUT1} ${INPUT2}
    Should Be Equal    ${SUITE.start_time}      ${datetime(2007, 9, 25, 21, 51)}
    Should Be Equal    ${SUITE.end_time}        ${datetime(2007, 9, 26, 1, 12, 30, 200000)}
    Should Be Equal    ${SUITE.elapsed_time}    ${timedelta(seconds=3*60*60 + 21*60 + 30.2)}

Combine with only start time
    Run Rebot    --starttime 20070925-2151    ${INPUT1} ${INPUT2}
    Should Be Equal    ${SUITE.start_time}      ${datetime(2007, 9, 25, 21, 51)}
    Should Be Equal    ${SUITE.end_time}        ${{datetime.datetime(2007, 9, 25, 21, 51) + $ORIG_ELAPSED}}
    Should Be Equal    ${SUITE.elapsed_time}    ${ORIG_ELAPSED}

Combine with only end time
    Run Rebot    --endtime 2010_01.01:12-33    ${INPUT1} ${INPUT2}
    Should Be Equal    ${SUITE.start_time}      ${{datetime.datetime(2010, 1, 1, 12, 33) - $ORIG_ELAPSED}}
    Should Be Equal    ${SUITE.end_time}        ${datetime(2010, 1, 1, 12, 33)}
    Should Be Equal    ${SUITE.elapsed_time}    ${ORIG_ELAPSED}

Recombining
    ${options} =    Catenate
    ...    --starttime 2007:09:25:21:51
    ...    --endtime 2007:09:26:01:12:30:200
    ...    --output ${COMBINED}
    Run Rebot Without Processing Output    ${options}    ${INPUT1} ${INPUT2}
    Run Rebot    ${EMPTY}    ${INPUT1} ${INPUT2} ${COMBINED}
    Should Be True     $SUITE.elapsed_time > datetime.timedelta(hours=3, minutes=21, seconds=30.2)

Omit time part altogether
    Run Rebot    --starttime 2007-10-01 --endtime 20071006    ${INPUT1} ${INPUT2}
    Should Be Equal    ${SUITE.start_time}      ${datetime(2007, 10, 1)}
    Should Be Equal    ${SUITE.end_time}        ${datetime(2007, 10, 6)}
    Should Be Equal    ${SUITE.elapsed_time}    ${timedelta(days=5)}

Start time and end time with single output
    Run Rebot    --starttime 20070925-2151 --endtime 20070925-2252    ${INPUT1}
    Should Be Equal    ${SUITE.start_time}      ${datetime(2007, 9, 25, 21, 51)}
    Should Be Equal    ${SUITE.end_time}        ${datetime(2007, 9, 25, 22, 52)}
    Should Be Equal    ${SUITE.elapsed_time}    ${timedelta(hours=1, minutes=1)}

Start time with single output
    Run Rebot    --starttime 20070925-2151    ${INPUT1}
    Should Be Equal    ${SUITE.start_time}      ${datetime(2007, 9, 25, 21, 51)}
    Should Be Equal    ${SUITE.end_time}        ${SINGLE_SUITE_ORIG_END}
    Should Be True     $SUITE.elapsed_time > $SINGLE_SUITE_ORIG_ELAPSED

End time with single output
    Run Rebot    --endtime '2023-09-07 19:31:01.234'    ${INPUT1}
    Should Be Equal    ${SUITE.start_time}      ${SINGLE_SUITE_ORIG_START}
    Should Be Equal    ${SUITE.end_time}        ${datetime(2023, 9, 7, 19, 31, 1, 234000)}
    Should Be True     $SUITE.elapsed_time < $SINGLE_SUITE_ORIG_ELAPSED

*** Keywords ***
Create Input Files
    Create Output With Robot    ${INPUT1}    ${EMPTY}    misc/normal.robot
    Create Output With Robot    ${INPUT2}    ${EMPTY}    misc/suites/tsuite1.robot
    Run Rebot    ${EMPTY}    ${INPUT1} ${INPUT2}
    Set Suite Variable    $ORIG_START    ${SUITE.start_time}
    Set Suite Variable    $ORIG_END    ${SUITE.end_time}
    Set Suite Variable    $ORIG_ELAPSED    ${SUITE.elapsed_time}
    Run Rebot    ${EMPTY}    ${INPUT1}
    Set Suite Variable    $SINGLE_SUITE_ORIG_START    ${SUITE.start_time}
    Set Suite Variable    $SINGLE_SUITE_ORIG_END    ${SUITE.end_time}
    Set Suite Variable    $SINGLE_SUITE_ORIG_ELAPSED    ${SUITE.elapsed_time}
