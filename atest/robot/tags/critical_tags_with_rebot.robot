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
    --CritiCal fa* -c ?aSS                            yes    yes

Critical As Combined Pattern
    --CritiCal nonexORfa* -c ?assANDforce             yes    yes

Non-Critical
    --noncritical pass                                no     yes

Non-Critical Not Matching
    -n these -n dont -n match                         yes    yes

Non-Critical As Pattern
    --NonCritiCal fa__* -n ?__ass                     no     no

Non-Critical As Combined Pattern
    --NonCri nonex_OR_fa* -n ?assANDforce             no     no

Critical And Non-Critical Matching Different Test
    -c pa*ss -n fai? -c nomatch                       yes    no

Critical And Non-Critical Matching Same Test
    -c force -n fail -c a -c b -c c -n x -n y -n z    yes    no

Critical And Non-Critical Matching Same Tag
    --critical force --noncritical f*                 no     no

*** Keywords ***
Run Test To Create Output
    Run Tests    --critical pass --noncritical fail    misc/pass_and_fail.robot
    Move File    ${OUT FILE}    ${INPUT FILE}

Test Criticality
    [Arguments]    ${options}    ${crit 1}    ${crit 2}
    Run Rebot    ${options}    ${INPUT FILE}
    ${tests} =    Get Elements    ${OUT FILE}    suite/test
    Test Status And Criticality Should Be    ${tests[0]}    PASS    ${crit 1}
    Test Status And Criticality Should Be    ${tests[1]}    FAIL    ${crit 2}

Test Status And Criticality Should Be
    [Arguments]    ${test}    ${status}    ${criticality}
    [Documentation]    Must check status and criticality directly from XML because re-processed model would not have same criticality
    Should Be Equal    ${test.getchildren()[-1].attrib['status']}    ${status}
    Should Be Equal    ${test.getchildren()[-1].attrib['critical']}    ${criticality}
