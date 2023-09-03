*** Settings ***
Library           OperatingSystem
Library           ParameterLibrary    after1with    after2with    WITH NAME    Params
Library           ParameterLibrary    after1    after2
Library           ParameterLibrary    xxx    yyy    with name    Won't work
Library           ParameterLibrary    xxx    yyy    zzz    as    Won't work

*** Test Cases ***
Import Library Normally After Importing With Name In Another Suite
    OperatingSystem.Should Exist    .
    ParameterLibrary.Parameters Should Be    after1    after2

Import Library With Name After Importing With Name In Another Suite
    Params.Parameters Should Be    after1with    after2with

Correct Error When Using Keyword From Same Library With Different Names Without Prefix 3
    [Documentation]    FAIL Multiple keywords with name 'Parameters' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}ParameterLibrary.Parameters
    ...    ${SPACE*4}Params.Parameters
    Parameters
