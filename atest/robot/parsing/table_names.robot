*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    parsing/table_names.robot
Resource        atest_resource.robot

*** Test Cases ***
Settings section
    Should Be Equal    ${SUITE.doc}    Testing different ways to write "Settings".
    Check Test Tags    Test Case    Settings

Variables section
    Check First Log Entry    Test Case     Variables
    Check First Log Entry    Test Cases    VARIABLES

Test Cases section
    Check Test Case    Test Case
    Check Test Case    Test Cases

Keywords section
    ${tc} =    Check Test Case    Test Case
    Check Log Message    ${tc.kws[1].kws[0].kws[0].msgs[0]}    "Keywords" was executed

Comments section
    Check Test Case    Comment section exist
    Length Should Be    ${ERRORS}    6

Section names are space sensitive
    ${path} =    Normalize Path    ${DATADIR}/parsing/table_names.robot
    Invalid Section Error    0    table_names.robot    43    * * * K e y w o r d * * *

Singular headers are deprecated
    Should Be Equal    ${SUITE.metadata['Singular headers']}    Deprecated
    Check Test Case    Singular headers are deprecated
    Deprecated Section Warning    1    table_names.robot    47    *** Setting ***    *** Settings ***
    Deprecated Section Warning    2    table_names.robot    49    *** variable***    *** Variables ***
    Deprecated Section Warning    3    table_names.robot    51    ***TEST CASE***    *** Test Cases ***
    Deprecated Section Warning    4    table_names.robot    54    *keyword           *** Keywords ***
    Deprecated Section Warning    5    table_names.robot    57    *** Comment ***    *** Comments ***

Invalid sections
    [Setup]    Run Tests    ${EMPTY}    parsing/invalid_table_names.robot
    ${tc} =    Check Test Case    Test in valid table
    ${path} =    Normalize Path    ${DATADIR}/parsing/invalid_tables_resource.robot
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Keyword in valid table
    Length Should Be    ${ERRORS}    4
    Invalid Section Error    0    invalid_table_names.robot        1     *** Error ***
    Invalid Section Error    1    invalid_table_names.robot        8     *** ***
    Invalid Section Error    2    invalid_table_names.robot        18    *one more table cause an error
    Error In File    3    parsing/invalid_table_names.robot        6     Error in file '${path}' on line 1: Unrecognized section header '*** ***'. Valid sections: 'Settings', 'Variables', 'Keywords' and 'Comments'.

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

Deprecated Section Warning
    [Arguments]    ${index}    ${file}    ${lineno}    ${used}    ${expected}
    Error In File    ${index}    parsing/${file}    ${lineno}
    ...    Singular section headers like '${used}' are deprecated. Use plural format like '${expected}' instead.
    ...    level=WARN
