*** Settings ***
Library           String

*** Variables ***
${LOWER}          qwertyuiopasdfghjklzxcvbnm
${UPPER}          QWERTYUIOPASDFGHJKLZXCVBNM
${LETTERS}        ${LOWER}${UPPER}
${NUMBERS}        1234567890

*** Test Cases ***
Generate Random String With Defaults
    ${result} =    Generate Random String
    String Lenght Should Be And It Should Consist Of    ${result}    8    ${LETTERS}${NUMBERS}

Generate Random String With Empty Length
    ${result} =    Generate Random String    ${EMPTY}    abc
    String Lenght Should Be And It Should Consist Of    ${result}    8    abc

Generate Random String From Non Default Characters
    Test Random String With    %=}$+^~*äö#    %=}$+^~*äö#

Generate Random String From Non Default Characters And [NUMBERS]
    Test Random String With    %=}$+^~*äö#${NUMBERS}    %=}$+^~*äö#[NUMBERS]
    Test Random String With    %=}$+^~*äö#${NUMBERS}    [NUMBERS]%=}$+^~*äö#
    Test Random String With    %=}$+^~*äö#${NUMBERS}    %=}[NUMBERS]$+^~*äö#

Generate Random String With [LOWER]
    Test Random String With    ${LOWER}    [LOWER]

Generate Random String With [UPPER]
    Test Random String With    ${UPPER}    [UPPER]

Generate Random String With [LETTERS]
    Test Random String With    ${LETTERS}    [LETTERS]

Generate Random String With [NUMBERS]
    Test Random String With    ${NUMBERS}    [NUMBERS]

*** Keywords ***
String Lenght Should Be And It Should Consist Of
    [Arguments]    ${string}    ${length}    ${allowed chars}
    Length Should Be    ${string}    ${length}
    FOR    ${i}    IN RANGE    0    ${length}
        Should Contain    ${allowed chars}    ${string[${i}]}
        ...    String '${string}' contains character '${string[${i}]}' which is not in allowed characters '${allowed chars}'.
    END

Test Random String With
    [Arguments]    ${expected characters}    ${given characters}
    ${result} =    Generate Random String    100    ${given characters}
    String Lenght Should Be And It Should Consist Of    ${result}    100    ${expected characters}
