*** Settings ***
Suite Setup       Create Output
Force Tags        regression    pybot    jybot
Test Template     Run Rebot With RemoveKeywords
Resource          remove_keywords_resource.robot
Library           String

*** Test Cases ***          rem1      rem2      etc.

Rational                    FOR       WUKS
                            PASSED    FOR
                            PASSED    WUKS
                            PASSED    WUKS      FOR

Irrational                  ALL       WUKS
                            ALL       FOR       PASSED
                            WUKS      FOR       FOR    WUKS


*** Keywords ***
Run Rebot With RemoveKeywords
    [Arguments]    @{options}
    ${rmkws}=    Catenate    SEPARATOR= --RemoveKeywords=    ${EMPTY}    @{options}
    Run Rebot    ${rmkws} --log log.html   ${INPUTFILE}
    Validate Log    @{options}
    Validate Tests

Validate Log
    [Arguments]    @{options}
    ${LOG}=    Get File    ${OUTDIR}/log.html
    : FOR    ${item}    IN    @{options}
    \   Should Not Contain    ${LOG}    -${item}

Validate Tests
    Check Suite Contains Tests    ${SUITE}    Passing    Failing
    ...    For when test fails    For when test passes
    ...    WUKS when test fails    WUKS when test passes
    ...    NAME when test fails    NAME when test passes
    ...    NAME with * pattern when test fails    NAME with * pattern when test passes
    ...    NAME with ? pattern when test fails    NAME with ? pattern when test passes

Create Output
    Create Output With Robot    ${INPUTFILE}    ${EMPTY}    cli/remove_keywords/all_combinations.robot

