*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/get_regexp_matches.robot
Resource          atest_resource.robot

*** Test Cases ***
Get Regexp Matches With No Match
    Check Test Case    ${TESTNAME}

Get Regexp Matches Without Group
    Check Test Case    ${TESTNAME}

Get Regexp Matches Insert Group Regex Without Groups
    Check Test Case    ${TESTNAME}

Get Regexp Matches Insert Group Regex With Group Name
    Check Test Case    ${TESTNAME}

Get Regexp Matches Insert Group Regex With Group Names
    Check Test Case    ${TESTNAME}

Get Regexp Matches Insert Group Regex With Group Index
    Check Test Case    ${TESTNAME}

Get Regexp Matches Insert Group Regex With Group Indexes
    Check Test Case    ${TESTNAME}

Get Regexp Matches Insert Group Regex With Group Name And Index
    Check Test Case    ${TESTNAME}
