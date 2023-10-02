*** Settings ***
Documentation     Some of these tests are testing same features as tests under core/resource_and_variable_imports.html. These tests should all be gone through and all tests moved under variables/.
Suite Setup       Run Tests    --variable PRIORITIES_1:CLI --variablefile ${VARFILE1} --variablefile ${VARFILE2}    variables/variable_priorities.robot
Resource          atest_resource.robot

*** Variables ***
${VARDIR}         atest/robot/variables${/}..${/}..${/}testdata${/}variables${/}resvarfiles
${VARFILE1}       ${VARDIR}${/}cli_vars.py
${VARFILE2}       ${VARDIR}${/}cli_vars_2.py:mandatory_argument

*** Test Cases ***
Individual CLI Variables Override All Other Variables
    Check Test Case    Individual CLI Variables Override All Other Variables

Variable Files From CLI Override All Variables In Test Data
    Check Test Case    Variable Files From CLI Override All Variables In Test Data

When Multiple Variable Files Are Given From CLI The First One Has Highest Priority
    Check Test Case    When Multiple Variable Files Are Given From CLI The First One Has Highest Priority

Variable Tables In test Case Files Override Variables From Resource And Variable Files It Imports
    Check Test Case    Variable Tables In test Case Files Override Variables From Resource And Variable Files It Imports

Variable Tables In Resource Files Override Variables From Resource And Variable Files It Imports
    Check Test Case    Variable Tables In Resource Files Override Variables From Resource And Variable Files It Imports

When Multiple Resource Or Variable Files Are Imported The First One Has Highest Priority
    Check Test Case    When Multiple Resource Or Variable Files Are Imported The First One Has Highest Priority

Variables With Different Priorities Are Seen Also In User Keywords
    Check Test Case    Variables With Different Priorities Are Seen Also In User Keywords

Variables Set During Test Execution Override All Variables In Their Scope
    Check Test Case    Variables Set During Test Execution Override All Variables In Their Scope
