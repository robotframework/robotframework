*** Settings ***
Documentation     Some of these tests are testing same features as tests under core/resource_and_variable_imports.html. These tests should all be gone through and all tests moved under variables/.
Resource          resvarfiles/resource.robot
Variables         resvarfiles/variables.py
Variables         resvarfiles/variables_2.py
Resource          resvarfiles/resource_3.robot

*** Variables ***
${PRIORITIES_1}    Variable Table in Test Case File
${PRIORITIES_2}    Variable Table in Test Case File
${PRIORITIES_3}    Variable Table in Test Case File

*** Test Cases ***
Individual CLI Variables Override All Other Variables
    Should Be Equal    ${PRIORITIES_1}    CLI

Variable Files From CLI Override All Variables In Test Data
    Should Be Equal    ${PRIORITIES_2}    Variable File from CLI

When Multiple Variable Files Are Given From CLI The First One Has Highest Priority
    Should Be Equal    ${PRIORITIES_2}    Variable File from CLI
    Should Be Equal    ${PRIORITIES_2B}    Second Variable File from CLI

Variable Tables In test Case Files Override Variables From Resource And Variable Files It Imports
    Should Be Equal    ${PRIORITIES_3}    Variable Table in Test Case File

Variable Tables In Resource Files Override Variables From Resource And Variable Files It Imports
    Should Be Equal    ${PRIORITIES_4}    Resource File
    Should Be Equal    ${PRIORITIES_5}    Second Resource File

When Multiple Resource Or Variable Files Are Imported The First One Has Highest Priority
    Should Be Equal    ${PRIORITIES_4}    Resource File
    Should Be Equal    ${PRIORITIES_4B}    Variable File
    Should Be Equal    ${PRIORITIES_4C}    Second Variable File
    Should Be Equal    ${PRIORITIES_4D}    Third Resource File

Variables With Different Priorities Are Seen Also In User Keywords
    Check Variables In User Keyword

Variables Set During Test Execution Override All Variables In Their Scope
    ${PRIORITIES_1} =    Set Variable    Set during execution
    Set Test Variable    $PRIORITIES_2    Set during execution
    Set Suite Variable    $PRIORITIES_3    Set during execution
    Set Global Variable    $PRIORITIES_4    Set during execution
    Should Be Equal    ${PRIORITIES_1}    Set during execution
    Should Be Equal    ${PRIORITIES_2}    Set during execution
    Should Be Equal    ${PRIORITIES_3}    Set during execution
    Should Be Equal    ${PRIORITIES_4}    Set during execution
    Set Variables In User Keyword

*** Keywords ***
Check Variables In User Keyword
    Should Be Equal    ${PRIORITIES_1}    CLI
    Should Be Equal    ${PRIORITIES_2}    Variable File from CLI
    Should Be Equal    ${PRIORITIES_3}    Variable Table in Test Case File
    Should Be Equal    ${PRIORITIES_4}    Resource File
    Should Be Equal    ${PRIORITIES_5}    Second Resource File

Set Variables In User Keyword
    ${PRIORITIES_5} =    Set Variable    Set during execution
    Should Be Equal    ${PRIORITIES_5}    Set during execution
