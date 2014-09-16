*** Settings ***
Library    ParameterLibrary    first    1    WITH NAME    First
Library    ParameterLibrary    second    2    WITH NAME    Second

*** Variables ***
${VARIABLE}       value

*** Test Cases ***
Import Library
    Import Library    String
    Get Line Count    foo
    Import Library    ParameterLibrary    ${VARIABLE}    ${42}    WITH NAME    Dynamic
    Dynamic.Parameters

Set Library Search Order
    Set Library Search Order    Second
    Parameters
    First.Parameters
    Set Library Search Order    NonExisting    Dynamic    First
    Parameters
