*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  parsing/table_names.robot
Resource        atest_resource.robot

*** Test Cases ***
Setting Table
    [Documentation]  Check Setting table and its synonyms Settings and Metadata
    Should Start With  ${SUITE.doc}  Testing that different synonyms for table names work.
    Check Test Tags  Test Case  Metadata  Settings

Variable Table
    [Documentation]  Check Variable table and its synonym Variables
    Check First Log Entry  Test Case  Variable
    Check First Log Entry  Test Cases  Variables

Test Case Table
    [Documentation]  Check Test Case table and its synonym Test Cases
    Check Test Case  Test Case
    Check Test Case  Test Cases

Keyword Table
    [Documentation]  Check Keyword table and its synonyms Keywords, User Keyword and User Keywords
    ${tc} =  Check Test Case  Test Case
    Check Log Message  ${tc.kws[1].kws[0].kws[0].kws[0].kws[0].msgs[0]}  'User Keywords' was executed

Invalid Tables
    [Documentation]  Check that tables with non-matching names, including empty names, are ignored.\nEmpty names used to cause issue 793.
    [Setup]  Run Tests  ${EMPTY}  parsing/invalid_table_names.robot parsing/invalid_table_names.html
    ${tc} =  Check test case  Test in valid plain text table
    Check log message  ${tc.kws[0].kws[0].msgs[0]}  Keyword in valid plain text table
    Check log message  ${tc.kws[1].kws[0].msgs[0]}  Keyword in valid plain text table in resource
    ${tc} =  Check test case  Test in valid HTML table
    Check log message  ${tc.kws[0].kws[0].msgs[0]}  Keyword in valid HTML table
    Check log message  ${tc.kws[1].kws[0].msgs[0]}  Keyword in valid HTML table in resource
    Stderr should be empty

*** Keywords ***
Check First Log Entry
    [Arguments]  ${test case name}  ${expected}
    ${tc} =  Check Test Case  ${test case name}
    Check Log Message  ${tc.kws[0].msgs[0]}  ${expected}

