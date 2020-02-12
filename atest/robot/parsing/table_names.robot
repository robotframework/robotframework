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
    Invalid Section Error    0    table_names.robot    43    * * * K e y w o r d * * *

Invalid Tables
    [Setup]    Run Tests    ${EMPTY}    parsing/invalid_table_names.robot
    ${tc} =    Check Test Case    Test in valid table
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Keyword in valid table
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    Keyword in valid table in resource
    Length Should Be    ${ERRORS}    5
    Invalid Section Error    0    invalid_table_names.robot        1     *** Error ***
    Invalid Section Error    1    invalid_table_names.robot        8     *** ***
    Invalid Section Error    2    invalid_table_names.robot        17    *one more table cause an error
    Invalid Section Error    3    invalid_tables_resource.robot    1     *** ***                 test and task=
    Invalid Section Error    4    invalid_tables_resource.robot    10    ***Resource Error***    test and task=

*** Keywords ***
Check First Log Entry
    [Arguments]    ${test case name}    ${expected}
    ${tc} =    Check Test Case    ${test case name}
    Check Log Message    ${tc.kws[0].msgs[0]}    ${expected}

Invalid Section Error
    [Arguments]    ${index}    ${file}    ${lineno}    ${header}    ${test and task}=, 'Test Cases', 'Tasks'
    Error In File    ${index}    parsing/${file}    ${lineno}
    ...    Unrecognized section header '${header}'.
    ...    Valid sections: 'Settings', 'Variables'${test and task},
    ...    'Keywords' and 'Comments'.
