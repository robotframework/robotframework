*** Settings ***
Variables    extended_assign_vars.py

*** Test Cases ***

Set attributes to Python object
    [Setup]    Should Be Equal    ${VAR.attr}-${VAR.attr2}    value-v2
    ${VAR.attr} =    Set Variable    new value
    ${ v a r . attr2 } =    Set Variable    nv2
    ${VAR.attr3} =    Set Variable    ${42}
    Should Be Equal    ${VAR.attr}-${VAR.attr2}-${VAR.attr3}    new value-NV2-42

Setting attribute to Java object
    [Setup]    Should Be Equal    ${JVAR.javaInteger}:${JVAR.javaProperty}    -1:default
    ${JVAR.javaInteger} =    Set Variable   ${42}
    ${JVAR.javaProperty} =    Set Variable   value
    Should Be Equal    ${JVAR.javaInteger}:${JVAR.javaProperty}    42:value

Set attribute not directly in base
    ${VAR.demeter.loves} =   Set Variable  this
    Should Be Equal    ${VAR.demeter.loves}    this
    Should Be Equal    ${VAR.demeter.hates}    THIS

Trying to set un-settable attribute
    [Documentation]    FAIL STARTS: Setting attribute 'not_settable' to variable '\${VAR}' failed: AttributeError:
    ${VAR.not_settable} =    Set Variable    whatever

Using extended syntax when base variable does not exists creates new variable
    ${new.var} =    Set Variable    value
    Should Be Equal    ${new.var}    value
    Variable Should Not Exist    ${new}

Overriding variable that has dot it its name is possible
    ${new.var} =    Set Variable    value
    ${new.var} =    Set Variable    new value
    Should Be Equal    ${new.var}    new value
    Variable Should Not Exist    ${new}

Strings and integers do not support extended assign
    [Template]    Extended assignment is disabled
    string
    ${42}
    ${1.0}

Attribute name must be valid
    ${VAR.} =    Set Variable    empty
    ${VAR.2nd} =    Set Variable    starts with number
    ${VAR.foo-bar} =    Set Variable    invalid char
    Should Be Equal    ${VAR.}    empty
    Should Be Equal    ${VAR.2nd}    starts with number
    Should Be Equal    ${VAR.foo-bar}    invalid char

Extended syntax is ignored with list variables
    @{list} =    Create List    1    2    3
    @{list.new} =    Create List    1    2    3
    Should Be Equal    ${list}    ${list.new}


*** Keywords ***
Extended assignment is disabled
    [Arguments]   ${value}
    ${var} =    Set Variable    ${value}
    ${var.xxx} =    Set Variable    creates new variable
    Should Be Equal    ${var.xxx}    creates new variable

