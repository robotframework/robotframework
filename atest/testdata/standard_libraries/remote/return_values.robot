*** Settings ***
Test Template     Argument Should Be Returned Correctly
Library           Remote    127.0.0.1:${PORT}

*** Test Cases ***
String
    'Hyvä tulos!'

Integer
    42

Float
    3.14

Boolean
    False

Datetime
    datetime.datetime(2023, 9, 14, 17, 30, 23)

List
    \[1, 2, 'lolme']

Dict
    {'a': 1, 'b': [2, 3]}


*** Keywords ***
Argument Should Be Returned Correctly
    [Arguments]    ${expected}
    ${expected} =    Evaluate    ${expected}
    ${result} =    Run Keyword    ${TEST NAME}
    Should Be Equal    ${result}    ${expected}
    Should Be True    isinstance($result, type($expected))    Result type ${{type($result)}} is wrong.
