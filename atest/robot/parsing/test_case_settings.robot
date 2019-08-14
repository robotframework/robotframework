*** Settings ***
Documentation     Validating parsing of test case settings. Using tags,
...               setups, teardowns and timeouts are tested elsewhere.
Suite Setup       Run Tests    ${EMPTY}    parsing/test_case_settings.robot
Resource          atest_resource.robot

*** Test Cases ***
Name
    ${tc} =    Check Test Case    Normal name
    Should Be Equal    ${tc.name}    Normal name

Names are not formatted
    ${tc} =    Check Test Case    test_case names are NOT _forMatted_
    Should Be Equal    ${tc.name}    test_case names are NOT _forMatted_

'...' as name is deprecated
    Check Test Case    ...
    Verify Error    0
    ...    Invalid syntax in test case '...':
    ...    Using '...' as test case name is deprecated.
    ...    It will be considered line continuation in Robot Framework 3.2.
    ...    level=WARN

Documentation
    Verify Documentation    Documentation in single line and column.

Documentation in multiple columns
    Verify Documentation    Documentation for this test case in multiple columns

Documentation in multiple rows
    Verify Documentation    1st logical line
    ...    is shortdoc.
    ...    ${EMPTY}
    ...    This documentation has multiple rows
    ...    and also multiple columns.

Documentation with variables
    Verify Documentation    Variables work in documentation since Robot 1.2.

Documentation with non-existing variables
    Verify Documentation
    ...    Starting from RF 2.1 \${NONEX} variables are just
    ...    left unchanged in all documentations. Existing ones
    ...    are replaced: "99999"

Documentation with escaping
    Verify Documentation    \${VERSION}\nc:\\temp\n\n\\

Name and documentation on console
    Check Stdout Contains    Normal name${SPACE * 59}| PASS |
    Check Stdout Contains    test_case names are NOT _forMatted_${SPACE * 35}| PASS |
    Check Stdout Contains    Documentation :: Documentation in single line and column.${SPACE * 13}| PASS |
    Check Stdout Contains    Documentation in multiple rows :: 1st logical line is shortdoc.${SPACE * 7}| PASS |
    Check Stdout Contains    Documentation with non-existing variables :: Starting from RF ${2}.1 ... | PASS |

Tags
    Verify Tags    force-1    test-1    test-2

Empty and NONE tags are ignored
    Verify Tags        force-1    test-1    test-2    test-3

Duplicate tags are ignored and first used format has precedence
    [Documentation]    Case, space and underscore insensitive
    Verify Tags        FORCE-1    Test_1    test 2

Tags in multiple rows
    Verify Tags        force-1    test-0    test-1    test-2    test-3    test-4    test-5

No own tags
    Verify Tags        default-1    default-2    default-3    force-1

Override default tags using empty setting
    Verify Tags        force-1

Override default tags using NONE
    Verify Tags        force-1

Tags with variables
    Verify Tags        force-1    test-1    test-2    test-3    test-4    test-5

Tags with non-existing variables
    Verify Tags         \${non_existing}    42    \@{non_existing}    force-1    test

Setup
    Verify Setup    Test case setup

Teardown
    Verify Teardown    Test case teardown

Default setup and teardown
    Verify Setup    Default setup
    Verify Teardown    Default teardown

Setup and teardown with variables
    Verify Setup    Logged using variables 1
    Verify Teardown    Logged using variables 2

Override setup and teardown using empty settings
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.setup}    ${NONE}
    Should Be Equal    ${tc.teardown}    ${NONE}

Override setup and teardown using NONE
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.setup}    ${NONE}
    Should Be Equal    ${tc.teardown}    ${NONE}

Setup and teardown with escaping
    Verify Setup    One backslash \\
    Verify Teardown    \${notvar} is not a variable

Template
    [Documentation]    Mainly tested elsewhere
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hello, world!
    Check Log Message    ${tc.kws[1].msgs[0]}    Hi, tellus!

Timeout
    Verify Timeout    1 day

Timeout with message
    Verify Timeout    2 minutes 3 seconds 456 milliseconds
    Verify Error    1
    ...    Invalid syntax in test case 'Timeout with message':
    ...    Using custom timeout messages is deprecated since
    ...    Robot Framework 3.0.1 and will be removed in future versions.
    ...    Message that was used is 'Message'.
    ...    level=WARN

Default timeout
    Verify Timeout    1 minute 39 seconds 999 milliseconds

Timeout with variables
    Verify Timeout    1 day 3 hours 46 minutes 39 seconds

Override timeout using empty setting
    Verify Timeout    ${NONE}

Override timeout using NONE
    Verify Timeout    ${NONE}

Invalid timeout
    Verify Timeout    invalid

Multiple settings
    Verify Documentation    Documentation for this test case
    Verify Tags             force-1    test-1    test-2
    Verify Setup            Test case setup
    Verify Teardown         Test case teardown
    Verify Timeout          12 seconds 345 milliseconds

Deprecated setting format
    Check Test Case    Invalid setting
    Verify Error    2
    ...    Invalid syntax in test case 'Invalid setting':
    ...    Setting 'Doc U Ment ation' is deprecated. Use 'Documentation' instead.
    ...    level=WARN

Invalid setting
    Check Test Case    ${TEST NAME}
    Verify Error    3
    ...    Invalid syntax in test case '${TEST NAME}':
    ...    Non-existing setting 'Invalid'.

*** Keywords ***
Verify Documentation
    [Arguments]    @{doc}
    ${tc} =    Check Test Case    ${TEST NAME}
    ${doc} =    Catenate    SEPARATOR=\n    @{doc}
    Should Be Equal    ${tc.doc}    ${doc}

Verify Tags
    [Arguments]    @{tags}
    Check Test Tags    ${TEST NAME}    @{tags}

Verify Setup
    [Arguments]    ${message}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.setup.name}    BuiltIn.Log
    Check Log Message    ${tc.setup.msgs[0]}    ${message}

Verify Teardown
    [Arguments]    ${message}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.teardown.name}    BuiltIn.Log
    Check Log Message    ${tc.teardown.msgs[0]}    ${message}

Verify Timeout
    [Arguments]    ${timeout}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.timeout}    ${timeout}

Verify Error
    [Arguments]    ${index}    @{message parts}    ${level}=ERROR
    ${path} =    Normalize Path    ${DATADIR}/parsing/test_case_settings.robot
    ${message} =    Catenate    Error in file '${path}':    @{message parts}
    Check Log Message    ${ERRORS}[${index}]    ${message}    ${level}
