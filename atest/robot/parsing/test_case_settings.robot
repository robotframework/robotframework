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

Name with variable
    ${tc} =    Check Test Case    Name with variables works since RF 3.2
    Should Be Equal    ${tc.name}    Name with variables works since RF 3.2

Name with non-existing variable
    ${tc} =    Check Test Case    Name with \${NON-EXISTING VARIABLE}
    Should Be Equal    ${tc.name}    Name with \${NON-EXISTING VARIABLE}

Name with escaped variable
    ${tc} =    Check Test Case    Name with \${ESCAPED} \${VARIABLE}
    Should Be Equal    ${tc.name}    Name with \${ESCAPED} \${VARIABLE}

Name with escapes
    [Documentation]    These names are not shown that nicely in log
    ${tc} =    Check Test Case    Name with escapes like '', '\n' and 'c:\path\temp'
    Should Be Equal    ${tc.name}    Name with escapes like '', '\n' and 'c:\path\temp'

Name with invalid escapes
    ${tc} =    Check Test Case    Name with invalid escapes like 'x' and 'uOOPS'
    Should Be Equal    ${tc.name}    Name with invalid escapes like 'x' and 'uOOPS'

Name with escaped escapes
    ${tc} =    Check Test Case    Name with escaped escapes like '\\', '\\n' , '\\x' and 'c:\\path\\temp'
    Should Be Equal    ${tc.name}    Name with escaped escapes like '\\', '\\n', '\\x' and 'c:\\path\\temp'

Documentation
    Verify Documentation    Documentation in single line and column.

Documentation in multiple columns
    Verify Documentation    Documentation${SPACE*4}for this test case${SPACE*4}in multiple columns

Documentation in multiple rows
    Verify Documentation    1st logical line
    ...    is shortdoc.
    ...
    ...    This documentation has multiple rows
    ...    and also${SPACE*4}multiple columns.
    ...
    ...    Newlines can also be added literally with "\n".
    ...    If a row ends with a newline
    ...    or backslash no automatic newline is added.
    ...
    ...    | table | =header= |
    ...    | foo${SPACE*3}|${SPACE*4}bar${SPACE*3}|
    ...    | ragged |

Documentation with variables
    Verify Documentation    Variables work in documentation since RF 1.2.

Documentation with non-existing variables
    Verify Documentation
    ...    Starting from RF 2.1 \${NONEX} variables are just
    ...    left unchanged in all documentations. Existing ones
    ...    are replaced: "99999"

Documentation with unclosed variables
    Verify Documentation    No closing curly at \${all     test=${TEST NAME} 1
    Verify Documentation    Not \${properly {closed}       test=${TEST NAME} 2
    Verify Documentation    2nd not \${properly}[closed    test=${TEST NAME} 3

Documentation with escaping
    Verify Documentation    \${VERSION}\nc:\\temp\n\n\\

Name and documentation on console
    Stdout Should Contain    Normal name${SPACE * 59}| PASS |
    Stdout Should Contain    test_case names are NOT _forMatted_${SPACE * 35}| PASS |
    Stdout Should Contain    Documentation :: Documentation in single line and column.${SPACE * 13}| PASS |
    Stdout Should Contain    Documentation in multiple rows :: 1st logical line is shortdoc.${SPACE * 7}| PASS |
    Stdout Should Contain    Documentation with non-existing variables :: Starting from RF ${2}.1 ... | PASS |

Tags
    Verify Tags    force-1    test-1    test-2

Empty and NONE tags are ignored
    Verify Tags        force-1    test-1    test-2    test-3

Duplicate tags are ignored and first used format has precedence
    [Documentation]    Case, space and underscore insensitive
    Verify Tags        force-1    Test_1    test 2

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

Setup and teardown with non-existing variables
    Check Test Case    ${TEST NAME}

Override setup and teardown using empty settings
    ${tc} =    Check Test Case    ${TEST NAME}
    Setup Should Not Be Defined     ${tc}
    Teardown Should Not Be Defined     ${tc}

Override setup and teardown using NONE
    ${tc} =    Check Test Case    ${TEST NAME}
    Setup Should Not Be Defined     ${tc}
    Teardown Should Not Be Defined     ${tc}

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

Setting not valid with tests
    Check Test Case    ${TEST NAME}

Small typo should provide recommendation
    Check Test Case    ${TEST NAME}


*** Keywords ***
Verify Documentation
    [Arguments]    @{doc}    ${test}=${TEST NAME}
    ${tc} =    Check Test Case    ${test}
    ${doc} =    Catenate    SEPARATOR=\n    @{doc}
    Should Be Equal    ${tc.doc}    ${doc}

Verify Tags
    [Arguments]    @{tags}
    Check Test Tags    ${TEST NAME}    @{tags}

Verify Setup
    [Arguments]    ${message}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.setup.full_name}    BuiltIn.Log
    Check Log Message    ${tc.setup.msgs[0]}    ${message}

Verify Teardown
    [Arguments]    ${message}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.teardown.full_name}    BuiltIn.Log
    Check Log Message    ${tc.teardown.msgs[0]}    ${message}

Verify Timeout
    [Arguments]    ${timeout}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.timeout}    ${timeout}
