*** Settings ***
Variables           list_and_dict_variable_file.py
Variables           list_and_dict_variable_file.py    LIST__inv_list    not a list
Variables           list_and_dict_variable_file.py    DICT__inv_dict    ${EXP LIST}

*** Variables ***
@{EXP LIST}         1    2    ${3}
@{EXP GENERATOR}    ${0}    ${1}    ${2}    ${3}    ${4}
&{NESTED}           key=value
&{EXP DICT}         a=${1}    ${2}=b    nested=${NESTED}
@{EXP KEYS}         a    b    c    d    e    f    g    h    i    j

*** Test Cases ***
Valid list
    Should Be Equal    ${LIST}    ${EXP LIST}

Valid dict
    Should Be Equal    ${DICT}    ${EXP DICT}

List is list
    Should Be Equal    ${TUPLE}    ${EXP LIST}
    Should Be True     ${TUPLE}    ['1', '2', 3]
    Should Be Equal    ${GENERATOR}    ${EXP GENERATOR}
    Should Be True     ${GENERATOR}    [0, 1, 2, 3, 4]
    ${list} =    Create List    @{GENERATOR}    @{GENERATOR}
    Should Be True    ${list} == [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]

Dict is dotted
    Should Be Equal    ${DICT.a}    ${1}
    Should Be Equal    ${DICT.nested.key}    value
    Should Be Equal    ${ORDERED.a}    ${97}

Dict is ordered
    ${keys} =    Create List    @{ORDERED}
    Should Be Equal    ${keys}    ${EXP KEYS}

Invalid list
    Variable Should Not Exist    ${INV LIST}

Invalid dict
    Variable Should Not Exist    ${INV DICT}

Scalar list likes can be used as list
    Should Be Equal    ${SCALAR LIST}    ${EXP LIST}
    ${list} =    Create List    @{SCALAR LIST}
    Should Be Equal    ${list}    ${EXP LIST}
    ${list} =    Create List    @{SCALAR TUPLE}
    Should Be Equal    ${list}    ${EXP LIST}
    Should Be Equal    ${SCALAR LIST}[0]    1
    Should Be Equal    ${SCALAR TUPLE}[-1]    ${3}

Scalar list likes are not converted to lists
    Should Not Be Equal    ${SCALAR TUPLE}    ${EXP LIST}
    Should Be True    ${SCALAR TUPLE} == tuple(${EXP LIST})
    Should Not Be Equal    ${SCALAR GENERATOR}    ${EXP GENERATOR}
    ${list} =    Create List    @{SCALAR GENERATOR}    @{SCALAR GENERATOR}
    Should Be Equal    ${list}    ${EXP GENERATOR}

Scalar dicts can be used as dicts
    Should Be Equal    ${SCALAR DICT}    ${EXP DICT}
    ${dict} =    Create Dictionary    &{SCALAR DICT}
    Should Be Equal    ${dict}    ${EXP DICT}
    Should Be Equal    ${SCALAR DICT}[a]    ${1}

Scalar dicts are not converted to DotDicts
    Variable Should Not Exist    ${SCALAR DICT.a}

Failing list
    [Documentation]    FAIL STARTS: Resolving variable '\@{FAILING GENERATOR()}' failed: ZeroDivisionError:
    Log Many   @{FAILING GENERATOR()}

Failing list in for loop
    [Documentation]    FAIL STARTS: Resolving variable '\@{FAILING GENERATOR()}' failed: ZeroDivisionError:
    FOR    ${i}    IN    @{FAILING GENERATOR()}
        Fail    Not executed
    END

Failing dict
    [Documentation]    FAIL Resolving variable '\&{FAILING DICT}' failed: Bang
    Log Many   &{FAILING DICT}

Open files are not lists
    [Documentation]    FAIL Value of variable '\@{OPEN FILE}' is not list or list-like.
    Log Many    @{OPEN FILE}

Closed files are not lists
    [Documentation]    FAIL Value of variable '\@{CLOSED FILE}' is not list or list-like.
    Log Many    @{CLOSED FILE}
