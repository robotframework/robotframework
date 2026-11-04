*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    parsing/test_metadata_setting.robot
Resource          atest_resource.robot

*** Test Cases ***
Tests get default metadata
    Metadata Should Be    Use defaults
    ...    Owner=QA Team    Priority=Normal    Alias=Task Metadata is an alias
    ...    Multi=Value in\nmultiple rows    Variable=resolved
    Should Be Empty    ${ERRORS}

Default can be overridden
    Metadata Should Be    Override default
    ...    Owner=QA Team    Priority=Critical    Alias=Task Metadata is an alias
    ...    Multi=Value in\nmultiple rows    Variable=resolved

New metadata can be added
    Metadata Should Be    Add new
    ...    Owner=QA Team    Priority=Normal    Alias=Task Metadata is an alias
    ...    Multi=Value in\nmultiple rows    Variable=resolved    Issue=4409

Default can be removed
    ${tc} =    Check Test Case    Remove default
    Should Not Contain    ${tc.metadata}    Owner
    Should Be Equal    ${tc.metadata}[Priority]    Normal

Removing is case, space and underscore insensitive
    ${tc} =    Check Test Case    Remove is normalized
    Should Not Contain    ${tc.metadata}    Owner

Removing non-existing metadata is not an error
    ${tc} =    Check Test Case    Remove non-existing
    Should Be Equal    ${tc.metadata}[Owner]    QA Team
    Should Be Empty    ${ERRORS}

Removing does not support patterns
    ${tc} =    Check Test Case    Remove does not support patterns
    Should Be Equal    ${tc.metadata}[Priority]    Normal

Escaped hyphen is used as a literal name
    ${tc} =    Check Test Case    Escaped hyphen is literal
    Should Be Equal    ${tc.metadata}[-Literal]    value
    Should Be Equal    ${tc.metadata}[Owner]    QA Team

Name from variable is never removal
    ${tc} =    Check Test Case    Name from variable is not removal
    Should Be Equal    ${tc.metadata}[-Owner]    value
    Should Be Equal    ${tc.metadata}[Owner]    QA Team

Metadata removed later in the same file is not set
    ${tc} =    Check Test Case    Use defaults
    Should Not Contain    ${tc.metadata}    Removed

In init files
    [Documentation]    Metadata is inherited recursively and lower levels can override
    ...                and remove individual items. Suite files do not affect each
    ...                other and an init file can have both `Metadata` and
    ...                `Test Metadata`.
    Run Tests    ${EMPTY}    parsing/test_metadata_directory
    Metadata Should Be    Inherited from init files and suite file
    ...    Owner=Parent Team    Priority=High    Suite File=Set in the suite file
    Metadata Should Be    Own metadata wins
    ...    Owner=Parent Team    Priority=Critical    Suite File=Set in the suite file
    Metadata Should Be    Remove inherited from parent init file
    ...    Priority=High    Suite File=Set in the suite file
    Metadata Should Be    Sibling suite file
    ...    Owner=Parent Team    Priority=Normal    Dropped=Removed by the child init file
    ${suite} =    Get Test Suite    Test Metadata Directory
    Should Be Equal    ${suite.metadata}[Suite Own]    Metadata of the directory suite itself
    Should Not Contain    ${suite.metadata}    Owner
    Should Be Empty    ${ERRORS}

Value is not allowed when removing
    Run Tests    ${EMPTY}    parsing/test_metadata_setting_errors.robot
    Error In File    0    parsing/test_metadata_setting_errors.robot    2
    ...    Setting 'Test Metadata' does not accept a value when removing metadata using the '-name' syntax, got 1.
    ${tc} =    Check Test Case    Value with removal in test is an error    FAIL
    ...    Setting 'Metadata' does not accept a value when removing metadata using the '-name' syntax, got 1.

*** Keywords ***
Metadata Should Be
    [Arguments]    ${name}    &{expected}
    ${tc} =    Check Test Case    ${name}
    Should Be Equal    ${tc.metadata}    ${expected}    formatter=repr
