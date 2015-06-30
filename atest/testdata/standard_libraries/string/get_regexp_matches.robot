*** Settings ***
Library           String

*** Variables ***
${TEXT IN COLUMNS}    abcdefg123\tabcdefg123\nabcdefg123\tabcdefg123
${REGULAR EXPRESSION}    abcdefg
${REGULAR EXPRESSION WITH GROUP}    ab(?P<group_name>cd)e(?P<group_name2>fg)
${UNMATCH REGULAR EXPRESSION}    hijk
${MATCH}    abcdefg
${GROUP MATCH}    cd
${SECOND INDEX GROUP}    fg

*** Test Cases ***
Get Regexp Matches With No Match
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${UNMATCH REGULAR EXPRESSION}
    ${expect_result}=    Create List
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Without Group
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION}
    ${expect_result}=    Create List    ${MATCH}    ${MATCH}    ${MATCH}    ${MATCH}
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Insert Group Regex Without Groups
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}
    ${expect_result}=    Create List    ${MATCH}    ${MATCH}    ${MATCH}    ${MATCH}
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Insert Group Regex With Group Name
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}    group_name
    ${expect_result}=    Create List    ${GROUP MATCH}    ${GROUP MATCH}    ${GROUP MATCH}    ${GROUP MATCH}
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Insert Group Regex With Group Names
    @{result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}    group_name    group_name2
    ${expect_result}=    Create List    ${GROUP MATCH}    ${GROUP MATCH}    ${GROUP MATCH}    ${GROUP MATCH}
    : FOR    ${first}    ${second}    IN ZIP    @{result}
    \    Should be Equal    ${first}    ${expect_result}

Get Regexp Matches Insert Group Regex With Group Index
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}    2
    ${expect_result}=    Create List    ${SECOND INDEX GROUP}    ${SECOND INDEX GROUP}    ${SECOND INDEX GROUP}    ${SECOND INDEX GROUP}
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Insert Group Regex With Group Indexes
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}    1    2
    ${expect_result}=    Create List    ${SECOND INDEX GROUP}    ${SECOND INDEX GROUP}    ${SECOND INDEX GROUP}    ${SECOND INDEX GROUP}
    Should be Equal    ${result}    ${expect_result}
