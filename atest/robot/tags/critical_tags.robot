*** Settings ***
Documentation     Setting critical and non-critical tags
Test Template     Test Criticality
Resource          atest_resource.robot

*** Variables ***
${MSG 000 211}    0 critical tests, 0 passed, 0 failed\n 2 tests total, 1 passed, 1 failed
${MSG 211 211}    2 critical tests, 1 passed, 1 failed\n 2 tests total, 1 passed, 1 failed
${MSG 110 211}    1 critical test, 1 passed, 0 failed\n 2 tests total, 1 passed, 1 failed
${MSG 101 211}    1 critical test, 0 passed, 1 failed\n 2 tests total, 1 passed, 1 failed

*** Test Cases ***
Neither Critical Nor Non-Critical
    ${EMPTY}    FAIL    ${MSG 211 211}

Critical
    --critical p_a_s_s    PASS    ${MSG 110 211}

Critical Not Matching
    -c nomatch    PASS    ${MSG 000 211}

Critical As Simple Pattern
    --critical faSTAR -c QUESTaSS    FAIL    ${MSG 211 211}

Critical As Combined Pattern
    --critical nonexORfaSTAR -c QUESTassANDforce    FAIL    ${MSG 211 211}

Non-Critical
    --noncritical pass    FAIL    ${MSG 101 211}

Non-Critical Not Matching
    -n these -n dont -n match    FAIL    ${MSG 211 211}

Non-Critical As Simple Pattern
    --NonCritical fa__STAR -n QUESTass    PASS    ${MSG 000 211}

Non-Critical As Combined Pattern
    --NonCritical nonexORfa__STAR -n QUESTassANDforce    PASS    ${MSG 000 211}

Critical And Non-Critical Matching Different Test
    --critical paSTARss --noncritical faiQUEST -c nomatch    PASS    ${MSG 110 211}

Critical And Non-Critical Matching Same Test
    --critical force --noncritical fail -c a -c b -c c -n x -n y -n z    PASS    ${MSG 110 211}

Critical And Non-Critical Matching Same Tag
    --critical force --noncritical fSTAR    PASS    ${MSG 000 211}

*** Keywords ***
Test Criticality
    [Arguments]    ${options}    ${exp status}    ${exp msg}
    Run Tests    ${options} --escape star:STAR --escape quest:QUEST    misc/pass_and_fail.robot
    Suite Status And Message Should Be    ${exp status}    ${exp msg}

Suite Status And Message Should Be
    [Arguments]    ${status}    ${message}
    [Documentation]    Must check status and message from stdout because re-processed suite would not have same criticality as during executiong
    Check Stdout Contains    Pass And Fail :: Some tests here ${SPACE * 36} | ${status} |\n${message}
