*** Settings ***
Resource          resvarfiles/resource.robot

*** Variables ***
${DEFINITION IN RESOURCE (1)}    ${STRING}
${DEFINITION IN RESOURCE (2)}    ${LIST[0]}! ${ONE ITEM[0]}
${DEFINITION IN RESOURCE (3)}    ${LIST WITH ESCAPES}
@{DEFINITION IN RESOURCE (4)}    @{LIST WITH ESCAPES}
${ORIGINAL DEFINITION IN SECOND RESOURCE}    ${DEFINITION IN SECOND RESOURCE}
${DEFINITION IN SECOND RESOURCE (local)}    ${PRIORITIES 5}

*** Test Cases ***
Scalar String
    Should Be Equal    ${STRING}    Hello world!
    Should Be Equal    I said: "${STRING}"    I said: "Hello world!"

Scalar Non-Strings
    Should Be True    ${INTEGER} == 42
    Should Be True    ${FLOAT} == -1.2
    Should Be True    ${BOOLEAN} == True
    Should Be True    ${NONE VALUE} == None

Scalar String With Escapes
    Should Be Equal    ${ESCAPES}    one \\ two \\\\ \${non_existing}

Empty Scalar String
    Should Be Equal    ${NO VALUE}    ${EMPTY}
    Should Be Equal    "${NO VALUE}${NO VALUE}"    ""

Scalar List
    Should Not Be Equal    ${LIST}    Hello world !
    Should Be True    ${LIST} == ['Hello','again', '?']
    Should Be Equal    ${LIST[0]}    Hello
    Should Be Equal    ${LIST[1]}    again
    Should Be Equal    ${LIST[2]}    ?

Scalar List With Non-Strings
    Should Be True    ${LIST WITH NON STRINGS} == [42, -1.2, True, None]

Scalar List With Escapes
    Test List With Escapes
    ...    ${LIST WITH ESCAPES [0]}    ${LIST WITH ESCAPES [1]}
    ...    ${LIST WITH ESCAPES [2]}    ${LIST WITH ESCAPES [3]}
    ${exp} =    Create List    one \\    two \\\\    three \\\\\\    \${non_existing}
    Should Be Equal    ${LIST WITH ESCAPES}    ${exp}
    Should Be True    ${LIST WITH ESCAPES} == ['one \\\\', 'two \\\\\\\\', 'three \\\\\\\\\\\\', '\${non_existing}']    Backslashes are doubled here because 'Should Be True' uses 'eval' internally

List with One Item
    Should Be True    ${ONE ITEM} == ['Hello again?']
    Should Be Equal    ${ONE ITEM}[0]    Hello again?

List With Multiple Items
    Should Be Equal    ${LIST}[0]    Hello
    Should Be Equal    ${LIST}[1]    again
    Should Be Equal    ${LIST}[2]    ?
    Should Be True    ${LIST} == ['Hello', 'again', '?']

List With Escapes
    Test List With Escapes    @{LIST WITH ESCAPES}

List Created From List With Escapes
    Should Be Equal    ${LIST CREATED FROM LIST WITH ESCAPES}[0]    one \\
    Should Be Equal    ${LIST CREATED FROM LIST WITH ESCAPES}[1]    two \\\\
    Should Be Equal    ${LIST CREATED FROM LIST WITH ESCAPES}[2]    three \\\\\\
    Should Be Equal    ${LIST CREATED FROM LIST WITH ESCAPES}[3]    \${non_existing}
    Should Be True    ${LIST WITH ESCAPES} == ${LIST CREATED FROM LIST WITH ESCAPES}
    Should Be Equal    ${LIST WITH ESCAPES}    ${LIST CREATED FROM LIST WITH ESCAPES}

List With No Items
    Should Be True    ${EMPTY LIST} == []
    ${ret} =    Catenate    @{EMPTY LIST}    @{EMPTY LIST}    only value    @{EMPTY LIST}
    Should Be Equal    ${ret}    only value

Variable Names Are Case Insensitive
    Should Be Equal    ${lowercase}    Variable name in lower case
    Should Be Equal    ${LOWERCASE}    Variable name in lower case
    Should Be Equal    ${LoWerCAse}    Variable name in lower case
    Should Be Equal    ${lowercase list}[0]    Variable name in lower case
    Should Be Equal    ${LOWERCASE LIST}[0]    Variable name in lower case
    Should Be Equal    ${lOWErcasE List}[0]    Variable name in lower case

Variable Names Are Space Insensitive
    Should Be Equal    ${SPACES}    Variable name with spaces
    Should Be Equal    ${ s P a C e s }    Variable name with spaces
    Should Be Equal    ${spaceslist}[0]    Variable name with spaces
    Should Be Equal    ${SP a c es li S T}[0]    Variable name with spaces

Variable Names Are Underscore Insensitive
    Should Be Equal    ${underscores}    Variable name with under scores
    Should Be Equal    ${_U N D_er_Scores__}    Variable name with under scores
    Should Be Equal    ${underscores list}[0]    Variable name with under scores
    Should Be Equal    ${ _u_N_de__r _S C ores__ LI__st }[0]    Variable name with under scores

Assign Mark With Scalar variable
    Should Be Equal    ${ASSIGN MARK}    This syntax works starting from 1.8

Assign Mark With List variable
    Should Be Equal    ${ASSIGN MARK LIST}[0]    This syntax works
    Should Be Equal    ${ASSIGN MARK LIST}[1]    starting
    Should Be Equal    ${ASSIGN MARK LIST}[2]    from
    Should Be Equal    ${ASSIGN MARK LIST}[3]    ${1.8}

Variables From Resource Files Can Be Used In Local Variable Table
    Should Be Equal    ${DEFINITION IN RESOURCE (1)}    Hello world!
    Should Be Equal    ${DEFINITION IN RESOURCE (2)}    Hello! Hello again?
    Test List With Escapes    @{DEFINITION IN RESOURCE (3)}
    Test List With Escapes    @{DEFINITION IN RESOURCE (4)}

Imported Resource Can Use Variables From Resources It Imports In Its Variable Table
    Should Be Equal    ${DEFINITION IN SECOND RESOURCE}    Second Resource File
    Should Be Equal    ${ORIGINAL DEFINITION IN SECOND RESOURCE}    Second Resource File
    Should Be Equal    ${DEFINITION IN SECOND RESOURCE (local)}    Second Resource File

*** Keywords ***
Test List With Escapes
    [Arguments]    ${item1}    ${item2}    ${item3}    ${item4}
    Should Be Equal    ${item1}    one \\
    Should Be Equal    ${item2}    two \\\\
    Should Be Equal    ${item3}    three \\\\\\
    Should Be Equal    ${item4}    \${non_existing}
