*** Settings ***
Documentation     Validating parsing of test case settings. Using tags,
...               setups, teardowns and timeouts are tested elsewhere.
Suite Setup       Run Tests    ${EMPTY}    parsing/test_case_settings.robot
Resource          atest_resource.robot

*** Test Cases ***
Name
    ${tc} =    Check Test Case    Normal name
    Should Be Equal    ${tc.name}    Normal name
    ${tc} =    Check Test Case    test_case names are NOT _forMatted_
    Should Be Equal    ${tc.name}    test_case names are NOT _forMatted_

Documentation
    Verify Documentation    Documentation for this test case

Documentaion using old [Document] setting
    Verify Documentation    This should be deprecated...

Documentation in multiple columns
    Verify Documentation    Documentation for this test case in multiple columns

Documentation in multiple rows
    Verify Documentation    1st line is shortdoc.
    ...    Documentation for this test case
    ...    in multiple rows.

Documentation multiple times
    Verify Documentation
    ...   This functionality should be deprecated. Documentation for this test case
    ...    multiple times.

Documentation with variables
    Verify Documentation    Variables work in documentation since Robot 1.2.

Documentation with non-existing variables
    Verify Documentation
    ...    Starting from RF 2.1 \${NONEX} variables are just
    ...    left unchanged in all documentations. Existing ones
    ...    are replaced: "99999"

Documentation with escaping
    Verify Documentation    \${XXX} c:\\temp${SPACE*2}\\

Name and documentation on console
    Check Stdout Contains    Documentation in multiple rows :: 1st line is shortdoc.${SPACE * 15}| PASS |

Tags
    Verify Tags    force-1    test-1    test-2

Empty and NONE tags are ignored
    Verify Tags        force-1    test-1    test-2    test-3

Duplicate tags are ignored and first used format has precedence
    [Documentation]    Case, space and underscore insensitive
    Verify Tags        FORCE-1    Test_1    test 2

Tags in multiple rows
    Verify Tags        force-1    test-0    test-1    test-2    test-3    test-4    test-5

Tags multiple times
    Verify Tags        deprecate    force-1    Should    this

No own tags
    Verify Tags        default-1    default-2    default-3    force-1

Override default tags using empty setting
    Verify Tags        force-1

Override default tags using NONE
    Verify Tags        force-1

Tags with variables
    [Documentation]    Check that variables work in test case tags and invalid variables are handled correctly
    Verify Tags        force-1    test-1    test-2    test-3    test-4    test-5

Tags with non-existing variables
    Verify Tags         \${non_existing}    \@{non_existing}    force-1

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

Invalid setting
    Check Test Case    ${TEST NAME}
    ${path} =    Normalize Path    ${DATADIR}/parsing/test_case_settings.robot
    Check Log Message    @{ERRORS}[4]
    ...    Error in file '${path}': Invalid syntax in test case '${TEST NAME}': Non-existing setting 'Invalid'.    ERROR

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
