*** Settings ***
Suite Setup  Import Resource  ${CURDIR}/import_resource_resource_1.robot

*** Variables ***
${VAR FROM IMPORT RESOURCE RESOURCE}  this should be overwritten
${COMMON VAR}  this should be overwritten

*** Test Cases ***
Import Resource In Suite Setup
    Should Be Equal  ${VAR FROM IMPORT RESOURCE RESOURCE}  value 1
    Should Be Equal  ${VAR FROM VARFILE 1}  VALUE FROM VARFILE 1
    KW From Import Resource Resource

Import Resource With Sub Resources
    Should Be Equal   ${VAR FROM IMPORT RESOURCE RESOURCE RESOURCE}  value x
    KW From Import Resource Resource Resource
    Verify OperatingSystem Is Imported
    Should Be Equal  ${VAR FROM VARFILE X}  Default varfile value

Import Resource In Test Case
    Import Resource  ${CURDIR}/import_resource_resource_2.robot
    Verify Test Case Resource Import
    Verify Test Case Resource Import In User Keyword

Import Resource In User Keyword
    Import Resource In User Keyword
    Verify User Keyword Resource Import
    Verify User Keyword Resource Import In User Keyword

Variables And Keywords Imported In Test Are Available In Next
    Verify Test Case Resource Import
    Verify User Keyword Resource Import

Re-Import Resource
    Set Test Variable  ${COMMON VAR}  original value
    Re-Import Resource And Verify Imports  1
    Re-Import Resource And Verify Imports  2
    Re-Import Resource And Verify Imports  1  upper
    Re-Import Resource And Verify Imports  2  upper

Import Resource Failure Is Catchable
    Run Keyword And Expect Error  Resource file 'non_existing.robot' does not exist.
    ...  Import Resource  non_existing.robot
    ${path} =    Normalize Path    ${CURDIR}/tags/__init__.robot
    Run Keyword And Expect Error  Initialization file '${path}' cannot be imported as a resource file.
    ...  Import Resource  ${path}

Import Resource From Pythonpath
    Run Keyword And Expect Error    *    Keyword should exist    PPATH KW
    Import Resource    resource_in_pythonpath.robot
    PPATH KW

*** Keywords ***
Import Resource In User Keyword
    Import Resource  ${CURDIR}/import_resource_resource_3.robot
    Verify User Keyword Resource Import

Verify User Keyword Resource Import
    Should Be Equal  ${VAR FROM IMPORT RESOURCE RESOURCE 3}  value 3
    KW From Import Resource Resource 3
    Verify String Is Imported

Verify User Keyword Resource Import In User Keyword
    Verify User Keyword Resource Import

Verify Test Case Resource Import
    Should Be Equal  ${VAR FROM IMPORT RESOURCE RESOURCE 2}  value 2
    KW From Import Resource Resource 2
    Verify Collections Is Imported

Verify Test Case Resource Import In User Keyword
    Verify Test Case Resource Import

Verify OperatingSystem Is Imported
    Directory Should Exist  ${CURDIR}

Verify Collections Is Imported
    Count Values In List  ${TEST TAGS}  whatever

Verify String Is Imported
    Split To Lines  whatever

Re-Import Resource And Verify Imports
    [Arguments]  ${num}  ${upper}=
    ${path} =  Set Variable  ${CURDIR}/import_resource_resource_${num}.robot
    ${path} =  Set Variable If  ${WINDOWS} and '${upper}' == 'upper'  ${path.upper()}  ${path}
    Import Resource  ${path}
    Should Be Equal  ${COMMON VAR}  resource ${num}
    KW From Import Resource Resource
