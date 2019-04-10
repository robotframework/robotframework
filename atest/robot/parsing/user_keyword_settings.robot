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

'...' as name is deprecated
    Check Test Case    ${TEST NAME}
    ${path} =    Normalize Path    ${DATADIR}/parsing/user_keyword_settings.robot
    ${message} =    Catenate
    ...    Error in file '${path}': Invalid syntax in keyword '...':
    ...    Using '...' as keyword name is deprecated.
    ...    It will be considered line continuation in Robot Framework 3.2.
    Check Log Message    ${ERRORS}[0]    ${message}    WARN

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

Documentation with escaping
    Verify Documentation    \${XXX} c:\\temp${SPACE*2}\\

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

Deprecatted setting format
    Check Test Case    Invalid setting
    ${path} =    Normalize Path    ${DATADIR}/parsing/user_keyword_settings.robot
    ${message} =    Catenate
    ...    Error in file '${path}':
    ...    Invalid syntax in keyword 'Invalid passing':
    ...    Setting 'Doc U Ment ation' is deprecated. Use 'Documentation' instead.
    Check Log Message    ${ERRORS}[2]    ${message}    WARN

Invalid setting
    Check Test Case    ${TEST NAME}
    ${path} =    Normalize Path    ${DATADIR}/parsing/user_keyword_settings.robot
    ${message} =    Catenate
    ...    Error in file '${path}':
    ...    Invalid syntax in keyword 'Invalid passing':
    ...    Non-existing setting 'Invalid Setting'.
    Check Log Message    ${ERRORS}[3]    ${message}    ERROR
    ${message} =    Catenate
    ...    Error in file '${path}':
    ...    Invalid syntax in keyword 'Invalid failing':
    ...    Non-existing setting 'invalid'.
    Check Log Message    ${ERRORS}[4]    ${message}    ERROR

*** Keywords ***
Verify Documentation
    [Arguments]    ${doc}    ${test}=${TEST NAME}
    ${tc} =    Check Test Case    ${test}
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
