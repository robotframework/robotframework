*** Settings ***
Documentation   NO RIDE because it could change WITH NAME format.
Library         OperatingSystem
Library         ParameterLibrary  before1  before2
Library         ParameterLibrary  before1with  before2with  With Name  Params
Library         libraryscope.Global  WITH NAME  GlobalScope
Library         libraryscope.Suite  with name  Suite Scope
Library         libraryscope.Test  WITH NAME  TEST SCOPE
Library         ParameterLibrary  ${1}  2

*** Test Cases ***
Import Library Normally Before Importing With Name In Another Suite
    OperatingSystem.Should Exist  ${CURDIR}
    ${p1}  ${p2} =  ParameterLibrary.Parameters
    Should Be Equal  ${p1}  before1
    Should Be Equal  ${p2}  before2

Import Library With Name Before Importing With Name In Another Suite
    ${p1}  ${p2} =  Params.Parameters
    Should Be Equal  ${p1}  before1with
    Should Be Equal  ${p2}  before2with

Correct Error When Using Keyword From Same Library With Different Names Without Prefix 1
    [Documentation]  FAIL Multiple keywords with name 'Parameters' found.\n  Give the full name of the keyword you want to use.\n  Found: 'ParameterLibrary.Parameters' and 'Params.Parameters'
    Parameters

Global Scope 1.1
    Register And Test Registered  Global Scope  G.1.1

Global Scope 1.2
    Register And Test Registered  Global Scope  G.1.2  G.1.1

Test Suite Scope 1.1
    Register And Test Registered  Suite Scope  S.1.1

Test Suite Scope 1.2
    Register And Test Registered  Suite Scope  S.1.2  S.1.1

Test Case Scope 1.1
    Register And Test Registered  Test Scope  T.1.1

Test Case Scope 1.2
    Register And Test Registered  Test Scope  T.1.2

*** Keywords ***
Register And Test Registered
    [Arguments]  ${scope}  ${reg}  @{exp}
    Run Keyword  ${scope}.Register  ${reg}
    Run Keyword  ${scope}.Should Be Registered  ${reg}  @{exp}

