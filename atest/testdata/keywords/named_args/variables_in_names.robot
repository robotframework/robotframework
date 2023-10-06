*** Settings ***
Library           python_library.py

*** Variables ***
${A}              a
${B}              b
${C}              c
${Ä}              ä
${SNOWMAN}        \u2603

*** Test Cases ***
Named arg name as variable
    ${result} =    Lib Mandatory And Named    ${A}=1    ${B}=2
    Should Be Equal    ${result}    1, 2
    ${result} =    Lib Mandatory And Named 2    ${C}=3    ${A}=1    ${B}=2
    Should Be Equal    ${result}    1, 2, 3

Named arg containing variable
    ${result} =    User Keyword    first ${A}rg=required
    Should Be Equal    ${result}    required, default
    ${result} =    User Keyword    first ${A}rg=1    ${A}-${B}-${C}=2
    Should Be Equal    ${result}    1, 2

Kwargs with variables in names
    ${result} =    Lib Kwargs    ${A}=A Value    ${B}=${2}
    Should Be Equal    ${result}    a:A Value, b:2 (int)
    ${result} =    Lib Mandatory Named And Kwargs    mandatory    ${C}=A Value
    Should Be Equal    ${result}    mandatory, 2 (int), c:A Value

Kwargs with variables with non-ASCII value in names
    ${result} =    Lib Kwargs    ${Ä}=1    ${SNOWMAN}=2
    Should Be Equal    ${result}    ${Ä}:1, ${SNOWMAN}:2

Escaping variable syntax in kwarg names
    ${result} =    Lib Kwargs    \${A}=A Value    \${non}=existing
    Should Be Equal    ${result}    \${A}:A Value, \${non}:existing

Named args and kwargs with variables
    ${result} =    Lib Mandatory Named And Kwargs    mandatory    ${B}=B
    Should Be Equal    ${result}    mandatory, B
    ${result} =    Lib Mandatory Named And Kwargs    ${C}=C    ${B}=B    ${A}=A    \${D}=D
    Should Be Equal    ${result}    A, B, \${D}:D, c:C

Non-existing variable as named arg name
    [Documentation]    FAIL Variable '${nonexisting}' not found.
    Lib Mandatory And Named    ${nonexisting}=non-existing

Non-existing variable as kwargs name
    [Documentation]    FAIL Variable '${nonexisting}' not found.
    Lib Kwargs    ${nonexisting}=non-existing

Variable with non-string value as named arg name
    ${result} =    Lib Mandatory And Named    ${1}=non-string
    Should Be Equal    ${result}    1=non-string, default

Variable with non-string value as kwargs name
    [Documentation]    FAIL Argument names must be strings.
    Lib Kwargs    ${1}=non-string

Equal sign in variable name
    ${timedelta} =    Evaluate    datetime.timedelta    modules=datetime
    ${result} =    User Keyword    ${timedelta(seconds=1)}    ${timedelta(hours=1)}
    Should Be Equal    ${result}    0:00:01, 1:00:00

*** Keywords ***
User Keyword
    [Arguments]    ${first arg}    ${a-b-c}=default
    RETURN    ${first arg}, ${a-b-c}
