*** Settings ***
Library    String
Library    Collections

*** Variables ***
${TEXT IN COLUMNS}    abcdefg123\tabcdefg123\nabcdefg123\tabcdefg123
${TEXT REPEAT COUNT}    4
${REGULAR EXPRESSION}    abcdefg
${REGULAR EXPRESSION WITH GROUP}    ab(?P<group_name>cd)e(?P<group_name2>fg)
${UNMATCH REGULAR EXPRESSION}    hijk
${MATCH}    abcdefg
${GROUP MATCH}    cd
${SECOND GROUP MATCH}    fg

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
    ${expect_result}=    Evaluate    [('${GROUP MATCH}', '${SECOND GROUP MATCH}') for i in range(${TEXT REPEAT COUNT})]
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Insert Group Regex With Group Index
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}    2
    ${expect_result}=    Create List    ${SECOND GROUP MATCH}    ${SECOND GROUP MATCH}    ${SECOND GROUP MATCH}    ${SECOND GROUP MATCH}
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Insert Group Regex With Group Indexes
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}    ${2}    ${1.0}
    ${expect_result}=    Evaluate    [('${SECOND GROUP MATCH}', '${GROUP MATCH}') for i in range(${TEXT REPEAT COUNT})]
    Should be Equal    ${result}    ${expect_result}

Get Regexp Matches Insert Group Regex With Group Name And Index
    ${result}=    Get Regexp Matches    ${TEXT IN COLUMNS}    ${REGULAR EXPRESSION WITH GROUP}    2    group_name
    ${expect_result}=    Evaluate    [('${SECOND GROUP MATCH}', '${GROUP MATCH}') for i in range(${TEXT REPEAT COUNT})]
    Should be Equal    ${result}    ${expect_result}
