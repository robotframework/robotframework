*** Settings ***
Library           Remote    127.0.0.1:${PORT}

*** Variables ***
${PORT}           8270
${NESTED DICT}    {'key': 'root', 'nested': {'key': 42, 'nested': {'key': 'leaf'}}}

*** Test Cases ***
Dicts are returned correctly
    [Template]    Returned dict should be correct
    {}                               Return Dict
    {'a': '1'}                       Return Dict    a=1
    {'a': 1, 'b': 2, 'c': 3}         Return Dict    a=${1}    b=${2}    c=${3}
    ${NESTED DICT}                   Return Nested Dict
    \[{'foo': 1}, ${NESTED DICT}]    Return Dict In List

Returned dicts are dot-accessible
    ${dict} =    Return Dict    key=value    foo=${2}
    Should Be Equal    ${dict.key}    value
    Should Be Equal    ${dict.foo}    ${2}
    ${dict} =    Return Nested Dict
    Should Be Equal    ${dict.key}    root
    Should Be Equal    ${dict.nested.key}    ${42}
    Should Be Equal    ${dict.nested.nested.key}    leaf
    ${d1}    ${d2} =    Return Dict In List
    Should Be Equal    ${d1.foo}    ${1}
    Should Be Equal    ${d2}    ${dict}
    Should Be Equal    ${d2.nested.nested.key}    leaf

*** Keywords ***
Returned dict should be correct
    [Arguments]    ${expected}    ${kw}    @{args}    &{kwargs}
    ${result} =    Run Keyword    ${kw}    @{args}    &{kwargs}
    ${expected} =    Evaluate    ${expected}
    Should Be Equal    ${result}    ${expected}
