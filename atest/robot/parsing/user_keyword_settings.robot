*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    parsing/user_keyword_settings.robot
Resource          atest_resource.robot

*** Test Cases ***
Name
    ${tc} =    Check Test Case    Normal name
    Should Be Equal  ${tc.kws[0].name}    Normal name
    ${tc} =    Check Test Case    Names are not formatted
    : FOR    ${kw}    IN    @{tc.kws}
    \    Should Be Equal    ${kw.name}  user_keyword nameS _are_not_ FORmatted

Documentation
    Verify Documentation    Documentation for this user keyword

Documentaion using old [Document] setting
    Verify Documentation    This should be deprecated...

Documentation in multiple columns
    Verify Documentation    Documentation for this user keyword in multiple columns

Documentation in multiple rows
    [Documentation]    Only first line is used when running tests
    Verify Documentation    1st line is shortdoc.

Documentation with variables
    Verify Documentation    Variables work in documentation since Robot 1.2.

Documentation with non-existing variables
    Verify Documentation    Starting from RF 2.1 \${NONEX} variables are just

Documentation with escaping
    Verify Documentation    \${XXX} c:\\temp${SPACE*2}\\

Arguments
    [Documentation]    Tested more thoroughly elsewhere.
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    mandatory-default-[]-{}
    Should Be True    ${tc.kws[0].args} == ('mandatory',)
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    1-2-[]-{}
    Should Be True    ${tc.kws[1].args} == ('1', '2')
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    1-2-[3, 4, 5]-{*'key': 6}    pattern=yes
    Should Be True    ${tc.kws[2].args} == ('\${1}', '\${2}', '\${3}', '\${4}', '\${5}', 'key=\${6}')

Teardown
    Verify Teardown    Keyword teardown

Teardown with variables
    Verify Teardown    Logged using variables

Teardown with escaping
    Verify Teardown    \${notvar} is not a variable

Return
    Check Test Case    ${TEST NAME}

Return using variables
    Check Test Case    ${TEST NAME}

Return multiple
    Check Test Case    ${TEST NAME}

Return with escaping
    Check Test Case    ${TEST NAME}

Timeout
    Verify Timeout    2 minutes 3 seconds

Timeout with message
    Verify Timeout    2 minutes 3 seconds 456 milliseconds

Timeout with variables
    Verify Timeout    1 day 4 hours 48 minutes

Invalid timeout
    Verify Timeout    invalid

Multiple settings
    Verify Documentation    Documentation for a user keyword
    Verify Teardown   Teardown World
    Verify Timeout  6 minutes

Invalid setting
    Check Test Case    ${TEST NAME}
    ${PATH} =    Normalize Path    ${DATADIR}/parsing/user_keyword_settings.robot
    Check Log Message    ${ERRORS[1]}
    ...    Error in file '${path}': Invalid syntax in keyword 'Invalid passing': Non-existing setting 'Invalid Setting'.    ERROR
    Check Log Message    ${ERRORS[2]}
    ...    Error in file '${path}': Invalid syntax in keyword 'Invalid failing': Non-existing setting 'invalid'.    ERROR

*** Keywords ***
Verify Documentation
    [Arguments]    ${doc}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].doc}    ${doc}

Verify Teardown
    [Arguments]    ${message}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].kws[-1].name}    BuiltIn.Log
    Check Log Message    ${tc.kws[0].kws[-1].msgs[0]}    ${message}

Verify Timeout
    [Arguments]    ${timeout}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].timeout}    ${timeout}
