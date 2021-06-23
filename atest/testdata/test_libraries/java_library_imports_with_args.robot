*** Settings ***
Library           MandatoryArgs    first arg    another arg

Library           DefaultArgs    m1    WITH NAME    D1
Library           DefaultArgs    m2    d1    WITH NAME    D2
Library           DefaultArgs    m3    1    2    WITH NAME    D3

Variables         java_vars_for_imports.py
Library           MandatoryArgs    ${42}    ${JAVA OBJECT}    WITH NAME    O1
Library           MandatoryArgs    @{LIST WITH OBJECTS}    WITH NAME    O2

Library           MandatoryArgs    too few
Library           DefaultArgs
Library           MandatoryArgs    too    many    args    here
Library           DefaultArgs    too    many    args    here    too
Library           MandatoryArgs    ${NON EXISTING}    hello

*** Test Cases ***
Mandatory arguments
    Verify arguments    MandatoryArgs    first arg    another arg

Default values
    Verify arguments    D1    m1
    Verify arguments    D2    m2    d1
    Verify arguments    D3    m3    1    2

Variables containing objects
    Verify arguments    O1    42    The name of the JavaObject
    Verify arguments    O2    {key=value}    true

*** Keywords ***
Verify arguments
    [Arguments]    ${lib}    @{expected args}
    ${expected} =    Catenate    SEPARATOR=${SPACE}&${SPACE}    @{expected args}
    ${actual} =    Run Keyword    ${lib}.Get Args
    Should be equal    ${actual}    ${expected}
