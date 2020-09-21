*** Settings ***
Library           String

*** Variables ***
${NSN}            nokia_siemens_networks
${WHITE SPACES}    hello\nworld\t${SPACE*5}again

*** Test Cases ***
Split String
    ${result} =    Split String    ${NSN}    _
    Result Should Contain Items In Given Order    ${result}    nokia    siemens    networks

Split String With Longer Separator
    ${result} =    Split String    1abc2abc3    abc
    Result Should Contain Items In Given Order    ${result}    1    2    3

Split String With none As Separator
    ${result} =    Split String    1none2none3    none
    Result Should Contain Items In Given Order    ${result}    1    2    3

Split String With Whitespaces and Separator Is None
    ${result} =    Split String    ${WHITE SPACES}
    Result Should Contain Items In Given Order    ${result}    hello    world    again

Split String With Max Split 0
    ${result} =    Split String    ${NSN}    _    0
    Result Should Contain Items In Given Order    ${result}    ${NSN}

Split String With Max Split 1
    ${result} =    Split String    ${NSN}    _    1
    Result Should Contain Items In Given Order    ${result}    nokia    siemens_networks

Split String With Empty Separator
    ${result} =    Split String    ${WHITE SPACES}    ${EMPTY}    -1
    Result Should Contain Items In Given Order    ${result}    hello    world    again

Split String With Empty String
    ${result} =    Split String    ${EMPTY}
    Should Be Empty    ${result}

Split String Separator not Found
    ${result} =    Split String    ${NSN}    NSN
    Result Should Contain Items In Given Order    ${result}    ${NSN}

Split String With Invalid Max Split
    [Documentation]    FAIL ValueError: Cannot convert 'max_split' argument 'invalid' to an integer.
    ${result} =    Split String    ${NSN}    NSN    invalid

Split String From Right
    ${result} =    Split String From Right    ${NSN}    _
    Result Should Contain Items In Given Order    ${result}    nokia    siemens    networks

Split String From Right With Longer Separator
    ${result} =    Split String From Right    1abc2abc3    abc
    Result Should Contain Items In Given Order    ${result}    1    2    3

Split String From Right With none As Separator
    ${result} =    Split String From Right    1none2none3    none
    Result Should Contain Items In Given Order    ${result}    1    2    3

Split String From Right With Whitespaces and Separator Is None
    ${result} =    Split String From Right    ${WHITE SPACES}
    Result Should Contain Items In Given Order    ${result}    hello    world    again

Split String From Right With Max Split 0
    ${result} =    Split String From Right    ${NSN}    _    0
    Result Should Contain Items In Given Order    ${result}    ${NSN}

Split String From Right With Max Split 1
    ${result} =    Split String From Right    ${NSN}    _    1
    Result Should Contain Items In Given Order    ${result}    nokia_siemens    networks

Split String From Right With Empty Separator
    ${result} =    Split String From Right    ${WHITE SPACES}    ${EMPTY}    -1
    Result Should Contain Items In Given Order    ${result}    hello    world    again

Split String From Right With Empty String
    ${result} =    Split String From Right    ${EMPTY}
    Should Be Empty    ${result}

Split String From Right Separator not Found
    ${result} =    Split String From Right    ${NSN}    NSN
    Result Should Contain Items In Given Order    ${result}    ${NSN}

Split String From Right With Invalid Max Split
    [Documentation]    FAIL ValueError: Cannot convert 'max_split' argument 'invalid' to an integer.
    ${result} =    Split String From Right    ${NSN}    NSN    invalid

Split String To Characters
    @{chars} =    Split String To Characters    ab 12
    Result Should Contain Items In Given Order    ${chars}    a    b    ${SPACE}    1    2

Split Empty String To Characters
    @{chars} =    Split String To Characters    ${EMPTY}
    Result Should Contain Items In Given Order    ${chars}

*** Keywords ***
Result Should Contain Items In Given Order
    [Arguments]    ${result list}    @{expected}
    ${length} =    Get Length    ${expected}
    Length Should Be    ${result list}    ${length}
    FOR    ${i}    IN RANGE    ${length}
        Should Be Equal    ${result list}[${i}]    ${expected}[${i}]
    END
