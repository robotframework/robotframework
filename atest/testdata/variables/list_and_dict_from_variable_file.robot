*** Settings ***
Variables           list_and_dict_variable_file.py
Variables           list_and_dict_variable_file.py    LIST__inv_list    not a list
Variables           list_and_dict_variable_file.py    DICT__inv_dict    ${EXP LIST}

*** Variables ***
@{EXP LIST}         1    2    ${3}
@{EXP GENERATOR}    ${0}    ${1}    ${2}    ${3}    ${4}
&{EXP DICT}         a=${1}    ${2}=b
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

Dict is dotted
    Should Be Equal    ${DICT.a}    ${1}
    Should Be Equal    ${ORDERED.a}    ${97}

Dict is ordered
    Should Be Equal    @{ORDERED}[0]    a
    Should Be Equal    @{ORDERED}[-1]    j
    Should Be Equal    ${ORDERED.keys()}    ${EXP KEYS}

Invalid list
    Variable Should Not Exist    ${INV LIST}

Invalid dict
    Variable Should Not Exist    ${INV DICT}
