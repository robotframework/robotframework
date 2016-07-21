*** Settings ***
Documentation     Setting critical and non-critical tags with Rebot.
Suite Setup       Run Test To Create Output
Suite Teardown    Remove File    ${INPUT FILE}
Resource          atest_resource.robot
Test Template     Test Criticality

*** Variables ***
${INPUT FILE}     %{TEMPDIR}/rebot-test-input.xml

*** Test Cases ***
Neither Critical Nor Non-Critical
    ${EMPTY}                                          yes    yes

Critical
    --critical pa__ss                                 yes    no

Critical Not Matching
    -c nomatch                                        no     no

Critical As Pattern
    --CritiCal faSTAR -c QUESTaSS                     yes    yes

Critical As Combined Pattern
    --CritiCal nonexORfaSTAR -c QUESTassANDforce      yes    yes

Non-Critical
    --noncritical pass                                no     yes

Non-Critical Not Matching
    -n these -n dont -n match                         yes    yes

Non-Critical As Pattern
    --NonCritiCal fa__STAR -n QUEST__ass              no     no

Non-Critical As Combined Pattern
    --NonCri nonex_OR_faSTAR -n QUESTassANDforce      no     no

Critical And Non-Critical Matching Different Test
    -c paSTARss -n faiQUEST -c nomatch                yes    no

Critical And Non-Critical Matching Same Test
    -c force -n fail -c a -c b -c c -n x -n y -n z    yes    no

Critical And Non-Critical Matching Same Tag
    --critical force --noncritical fSTAR              no     no

*** Keywords ***
Run Test To Create Output
    Run Tests    --critical pass --noncritical fail    misc/pass_and_fail.robot
    Move File    ${OUT FILE}    ${INPUT FILE}

Test Criticality
    [Arguments]    ${options}    ${crit 1}    ${crit 2}
    Run Rebot    ${options} --escape star:STAR --escape quest:QUEST    ${INPUT FILE}
    ${tests} =    Get Elements    ${OUT FILE}    suite/test
    Test Status And Criticality Should Be    ${tests[0]}    PASS    ${crit 1}
    Test Status And Criticality Should Be    ${tests[1]}    FAIL    ${crit 2}

Test Status And Criticality Should Be
    [Arguments]    ${test}    ${status}    ${criticality}
    [Documentation]    Must check status and criticality directly from XML because re-processed model would not have same criticality
    Should Be Equal    ${test.getchildren()[-1].attrib['status']}    ${status}
    Should Be Equal    ${test.getchildren()[-1].attrib['critical']}    ${criticality}
