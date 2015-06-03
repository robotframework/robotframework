*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/get_regexp_matches.robot
Force Tags        pybot    jybot    regression
Resource          atest_resource.robot

*** Variables ***
${TEXT IN COLUMNS}    abcdefg123\tabcdefg123\nabcdefg123\tabcdefg123
${REGULAR EXPRESSION}    abcdefg
${REGULAR EXPRESSION WITH GROUP}    ab(?P<group_name>cd)e(fg)
${UNMATCH REGULAR EXPRESSION}    hijk
${MATCH}          abcdefg
${GROUP MATCH}    cd

*** Test Cases ***
Get Regexp Matches With No Match
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${UNMATCH REGULAR EXPRESSION}
    ${expect_result}=    Create List
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Without Group
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION}
    ${expect_result}=    Create List    ${MATCH}    ${MATCH}    ${MATCH}    ${MATCH}
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Group Regex Without Group Name
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}
    ${expect_result}=    Create List    ${MATCH}    ${MATCH}    ${MATCH}    ${MATCH}
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Group Regex With Group Name
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}    group_name
    ${expect_result}=    Create List    ${GROUP MATCH}    ${GROUP MATCH}    ${GROUP MATCH}    ${GROUP MATCH}
    Should be Equal    ${result}    ${expect_result}
