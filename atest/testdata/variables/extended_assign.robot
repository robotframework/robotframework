*** Settings ***
Variables    extended_assign_vars.py
Library      Collections

*** Variables ***
&{DICT}      key=value

*** Test Cases ***
Set attributes to Python object
    [Setup]    Should Be Equal    ${VAR.attr}-${VAR.attr2}    value-v2
    ${VAR.attr} =    Set Variable    new value
    ${ v a r . attr2 } =    Set Variable    nv2
    ${VAR.attr3} =    Set Variable    ${42}
    Should Be Equal    ${VAR.attr}-${VAR.attr2}-${VAR.attr3}    new value-NV2-42

Set nested attribute
    ${VAR.demeter.loves} =   Set Variable    this
    Should Be Equal    ${VAR.demeter.loves}    this
    Should Be Equal    ${VAR.demeter.hates}    THIS

Set nested attribute when parent uses item access
    &{body} =    Evaluate     {'data': [{'name': 'old value'}]}
    ${body.data[0].name} =    Set Variable    new value
    Should Be Equal    ${body.data[0].name}    new value

Set item to list attribute
    &{body} =                Evaluate        {'data': [0, 1, 2, 3]}
    ${body.data}[${0}] =     Set Variable    firstVal
    ${body.data}[-1] =       Set Variable    lastVal
    ${body.data}[1:3] =      Create List     ${98}        middle    ${99}
    Lists Should Be Equal    ${body.data}    ${{['firstVal', 98, 'middle', 99, 'lastVal']}}

Set item to dict attribute
    &{body} =                        Evaluate              {'data': {'key': 'val', 0: 1}}
    ${body.data}[key] =              Set Variable          newVal
    ${body.data}[${0}] =             Set Variable          ${2}
    ${body.data}[newKey] =           Set Variable          newKeyVal
    Dictionaries Should Be Equal     ${body.data}          ${{{'key': 'newVal', 0: 2, 'newKey': 'newKeyVal'}}}

Set using @-syntax
    [Documentation]    FAIL Setting '\@{VAR.fail}' failed: Expected list-like value, got string.
    @{DICT.key} =    Create List    1    2    3
    Should Be Equal    ${DICT}    ${{{'key': ['1', '2', '3']}}}
    @{VAR.list: int} =    Create List    1    2    3
    Should Be Equal    ${VAR.list}    ${{[1, 2, 3]}}
    @{VAR.fail} =    Set Variable    not a list

Set using &-syntax
    [Documentation]    FAIL Setting '\&{DICT.fail}' failed: Expected dictionary-like value, got integer.
    &{VAR.dict} =    Create Dictionary    key=value
    Should Be Equal    ${VAR.dict}    ${{{'key': 'value'}}}
    Should Be Equal    ${VAR.dict.key}    value
    &{DICT.key: int=float} =    Create Dictionary    1=2.3    ${4.0}=${5.6}
    Should Be Equal    ${DICT}    ${{{'key': {1: 2.3, 4: 5.6}}}}
    Should Be Equal    ${DICT.key}[${1}]    ${2.3}
    &{DICT.fail} =    Set Variable    ${666}

Trying to set un-settable attribute
    [Documentation]    FAIL STARTS: Setting '\${VAR.not_settable}' failed: AttributeError:
    ${VAR.not_settable} =    Set Variable    whatever

Un-settable attribute error is catchable
    [Documentation]    FAIL GLOB:
    ...    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Setting '\${VAR.not_settable}' failed: AttributeError: *
    ...
    ...    2) AssertionError
    Run Keyword And Expect Error
    ...    Setting '\${VAR.not_settable}' failed: AttributeError: *
    ...    Setting unsettable attribute
    [Teardown]    Run Keywords    Setting unsettable attribute    Fail

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

*** Keywords ***
Extended assignment is disabled
    [Arguments]   ${value}
    ${var} =    Set Variable    ${value}
    ${var.xxx} =    Set Variable    creates new variable
    Should Be Equal    ${var.xxx}    creates new variable

Setting unsettable attribute
    ${VAR.not_settable} =    Set Variable    fails
