*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    parsing/table_names.robot
Resource        atest_resource.robot

*** Test Cases ***
Setting Table
    Should Be Equal    ${SUITE.doc}    Testing different ways to write "Setting(s)".
    Check Test Tags    Test Case    Settings

Variable Table
    Check First Log Entry    Test Case    Variable
    Check First Log Entry    Test Cases    Variables

Test Case Table
    Check Test Case    Test Case
    Check Test Case    Test Cases

Keyword Table
    ${tc} =    Check Test Case    Test Case
    Check Log Message    ${tc.kws[1].kws[0].kws[0].msgs[0]}    "Keywords" was executed

Comment Table
    Check Test Case    Comment tables exist
    Length Should Be    ${ERRORS}    1

Section Names Are Space Sensitive
    ${path} =    Normalize Path    ${DATADIR}/parsing/table_names.robot
    Validate Invalid Table Error    0    table_names.robot    43    K e y w o r d

Invalid Tables
    [Documentation]    Unrecognized tables should cause error
    [Setup]    Run Tests    ${EMPTY}    parsing/invalid_table_names.robot
    ${tc} =    Check Test Case    Test in valid table
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Keyword in valid table
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    Keyword in valid table in resource
    Length Should Be    ${ERRORS}    5
    Validate Invalid Table Error    0    invalid_table_names.robot        1     Error
    Validate Invalid Table Error    1    invalid_table_names.robot        8     ${EMPTY}
    Validate Invalid Table Error    2    invalid_table_names.robot        17    one more table cause an error
    Validate Invalid Table Error    3    invalid_tables_resource.robot    1     ${EMPTY}
    Validate Invalid Table Error    4    invalid_tables_resource.robot    10    Resource Error

*** Keywords ***
Check First Log Entry
    [Arguments]    ${test case name}    ${expected}
    ${tc} =    Check Test Case    ${test case name}
    Check Log Message    ${tc.kws[0].msgs[0]}    ${expected}

Validate Invalid Table Error
    [Arguments]    ${index}    ${file}    ${lineno}    ${header}
    Error In File    ${index}    parsing/${file}    ${lineno}
    ...    Unrecognized section header '${header}'.
    ...    Available headers for data: 'Setting(s)', 'Variable(s)', 'Test Case(s)',
    ...    'Task(s)' and 'Keyword(s)'. Use 'Comment(s)' to embedded additional data.
