*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/get_regexp_matches.robot
Force Tags        pybot    jybot    regression
Resource          atest_resource.robot

*** Test Cases ***
Get Regexp Matches With No Match
    Check Test Case    ${TESTNAME}

Get Regexp Matches Without Group
    Check Test Case    ${TESTNAME}

Get Regexp Matches Group Regex Without Group Name
    Check Test Case    ${TESTNAME}

Get Regexp Matches Group Regex With Group Name
    Check Test Case    ${TESTNAME}