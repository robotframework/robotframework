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
    String Length Should Be And It Should Consist Of    ${result}    8    ${LETTERS}${NUMBERS}

Generate Random String With Empty Length
    ${result} =    Generate Random String    ${EMPTY}    abc
    String Length Should Be And It Should Consist Of    ${result}    8    abc

Generate Random String With Random Length
    FOR    ${i}    IN RANGE    0    20
        ${result} =    Generate Random String    5-10
        String Length Should Be Within    ${result}    5    10
    END

Generate Random String With Invalid Ranges
    FOR    ${range}    IN     5-    foo-10    5-bar    foo-bar    -    5--10    1-2-3
        Run Keyword And Expect Error    ValueError: Cannot convert 'length' argument '${range}' to an integer.
        ...    Generate Random String    ${range}
    END

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
String Length Should Be And It Should Consist Of
    [Arguments]    ${string}    ${length}    ${allowed chars}
    Length Should Be    ${string}    ${length}
    FOR    ${i}    IN RANGE    0    ${length}
        Should Contain    ${allowed chars}    ${string[${i}]}
        ...    String '${string}' contains character '${string[${i}]}' which is not in allowed characters '${allowed chars}'.
    END

String Length Should Be Within
    [Arguments]     ${string}    ${lower limit}    ${upper limit}
    ${length} =    Get Length    ${string}
    Should Be True    ${lower limit} <= ${length} <= ${upper limit}

Test Random String With
    [Arguments]    ${expected characters}    ${given characters}
    ${result} =    Generate Random String    100    ${given characters}
    String Length Should Be And It Should Consist Of    ${result}    100    ${expected characters}
