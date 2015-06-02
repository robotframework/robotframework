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
    Should be Equal    ${result}    []

Get Regexp Matches Without Group
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION}
    Should be Equal    ${result}    ${MATCH}

Get Regexp Matches Group Regex Without Group Name
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}
    Should be Equal    ${result}    ${MATCH}

Get Regexp Matches Group Regex With Group Name
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}    group_name
    Should be Equal    ${result}    ${GROUP MATCH}
