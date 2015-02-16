*** Settings ***
Documentation   NO RIDE because it could change WITH NAME format.
Library         OperatingSystem
Library         ParameterLibrary  after1with  after2with  With Name  Params
Library         ParameterLibrary  after1  after2

*** Test Cases ***
Import Library Normally After Importing With Name In Another Suite
    OperatingSystem.Should Exist  ${CURDIR}
    ${p1}  ${p2} =  ParameterLibrary.Parameters
    Should Be Equal  ${p1}  after1
    Should Be Equal  ${p2}  after2

Import Library With Name After Importing With Name In Another Suite
    ${a1}  ${a2} =  Params.Parameters
    Should Be Equal  ${a1}  after1with
    Should Be Equal  ${a2}  after2with

Correct Error When Using Keyword From Same Library With Different Names Without Prefix 3
    [Documentation]  FAIL Multiple keywords with name 'Parameters' found.\
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}ParameterLibrary.Parameters
    ...    ${SPACE*4}Params.Parameters
    Parameters
