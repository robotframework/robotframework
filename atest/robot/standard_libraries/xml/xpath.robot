*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/xpath.robot
Test Setup       Make Tests Requiring ET 1.3 Non-Critical If Requirement Not Met
Force Tags       regression    pybot    jybot
Resource         xml_resource.robot

*** Test Cases ***

Tag
    Check Test Case    ${TESTNAME}

Path
    Check Test Case    ${TESTNAME}

Path matching multiple elements
    Check Test Case    ${TESTNAME}

'*'
    Check Test Case    ${TESTNAME}

'.'
    Check Test Case    ${TESTNAME}

'//'
    Check Test Case    ${TESTNAME}

'//' matching multiple elements
    Check Test Case    ${TESTNAME}

'..'
    [Tags]    X-Requires-ET-1.3
    Check Test Case    ${TESTNAME}

'[@attrib]'
    [Tags]    X-Requires-ET-1.3
    Check Test Case    ${TESTNAME}

'[@attrib="value"]'
    [Tags]    X-Requires-ET-1.3
    Check Test Case    ${TESTNAME}

'[tag]'
    [Tags]    X-Requires-ET-1.3
    Check Test Case    ${TESTNAME}

'[position]'
    [Tags]    X-Requires-ET-1.3
    Check Test Case    ${TESTNAME}

Stacked predicates
    [Tags]    X-Requires-ET-1.3
    Check Test Case    ${TESTNAME}

Non-ASCII tag names
    Check Test Case    ${TESTNAME}

More complex non-ASCII xpath
    [Tags]    X-Requires-ET-1.3
    Check Test Case    ${TESTNAME}

Warning when using more complex non-ASCII xpath with interpreter < 2.7
    Run Keyword If ET < 1.3    Verify Non-ASCII xpath error

Evaluate xpath does not work
    Check Test Case    ${TESTNAME}

*** Keywords ***
Make Tests Requiring ET 1.3 Non-Critical If Requirement Not Met
    Run Keyword If    'X-Requires-ET-1.3' in @{TEST TAGS}
    ...    Run Keyword If ET < 1.3    Remove Tags    regression

Run Keyword If ET < 1.3
    [Arguments]    ${kw}    @{args}
    Run Keyword If    '${SUITE.metadata["ET Version"]}' < '1.3'    ${kw}    @{args}

Verify Non-ASCII xpath error
    ${tc}=    Get Test Case    More complex non-ASCII xpath
    ${msg}=    Catenate
    ...    XPATHs containing non-ASCII characters and other than tag names
    ...    do not always work with Python/Jython versions prior to 2.7.
    ...    Verify results manually and consider upgrading to 2.7.
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    ${msg}    WARN
