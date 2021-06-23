*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    parsing/user_keyword_settings.robot
Resource          atest_resource.robot

*** Test Cases ***
Name
    ${tc} =    Check Test Case    Normal name
    Should Be Equal  ${tc.kws[0].name}    Normal name

Names are not formatted
    ${tc} =    Check Test Case    Names are not formatted
    FOR    ${kw}    IN    @{tc.kws}
        Should Be Equal    ${kw.name}  user_keyword nameS _are_not_ FORmatted
    END

No documentation
    Verify Documentation    ${EMPTY}    test=Normal name

Documentation
    Verify Documentation    Documentation for this user keyword

Documentation in multiple columns
    Verify Documentation    Documentation for this user keyword in multiple columns

Documentation in multiple rows
    Verify Documentation    1st line is shortdoc.

Short doc consists of first logical, not physical, line
    Verify Documentation    1st logical line is shortdoc.\nIt can be split to\nmultiple\nphysical\nlines.

Documentation with variables
    Verify Documentation    Variables work in documentation since Robot 1.2.

Documentation with non-existing variables
    Verify Documentation    Starting from RF 2.1 \${NONEX} variables are left unchanged.

Documentation with unclosed variables
    Verify Documentation    Not \${closed

Documentation with escaping
    Verify Documentation    \${XXX} - c:\\temp -${SPACE*2}- \\

Arguments
    [Documentation]    Tested more thoroughly elsewhere.
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    mandatory
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    default
    Should Be True       ${tc.kws[0].args} == ('mandatory',)
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    1
    Check Log Message    ${tc.kws[1].kws[0].msgs[1]}    2
    Should Be True       ${tc.kws[1].args} == ('1', '2')
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    1
    Check Log Message    ${tc.kws[2].kws[0].msgs[1]}    2
    Check Log Message    ${tc.kws[2].kws[0].msgs[2]}    3
    Check Log Message    ${tc.kws[2].kws[0].msgs[3]}    4
    Check Log Message    ${tc.kws[2].kws[0].msgs[4]}    5
    Check Log Message    ${tc.kws[2].kws[0].msgs[5]}    key=6
    Should Be True       ${tc.kws[2].args} == ('\${1}', '\${2}', '\${3}', '\${4}', '\${5}', 'key=\${6}')

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
    Error In File    0    parsing/user_keyword_settings.robot    195
    ...    Non-existing setting 'Invalid Setting'.
    Error In File    1    parsing/user_keyword_settings.robot    199
    ...    Non-existing setting 'invalid'.

Small typo should provide recommendation
    Check Test Case    ${TEST NAME}
    Error In File    2    parsing/user_keyword_settings.robot    203
    ...    SEPARATOR=\n
    ...    Non-existing setting 'Doc Umentation'. Did you mean:
    ...    ${SPACE*4}Documentation

*** Keywords ***
Verify Documentation
    [Arguments]    ${doc}    ${test}=${TEST NAME}
    ${tc} =    Check Test Case    ${test}
    Should Be Equal    ${tc.kws[0].doc}    ${doc}

Verify Teardown
    [Arguments]    ${message}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].teardown.name}    BuiltIn.Log
    Check Log Message    ${tc.kws[0].teardown.msgs[0]}    ${message}

Verify Timeout
    [Arguments]    ${timeout}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].timeout}    ${timeout}
