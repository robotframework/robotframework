*** Settings ***
Resource          resource_for_variable_table_in_resource_file.robot

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

List with One Item
    Should Be True    ${ONE ITEM} == ['Hello again?']
    Should Be Equal    ${ONE ITEM}[0]    Hello again?

List With Multiple Items
    Should Be Equal    ${LIST}[0]    Hello
    Should Be Equal    ${LIST}[1]    again
    Should Be Equal    ${LIST}[2]    ?
    Should Be True    ${LIST} == ['Hello', 'again', '?']

List With Escapes
    Should Be Equal    ${LIST WITH ESCAPES}[0]    one \\
    Should Be Equal    ${LIST WITH ESCAPES}[1]    two \\\\
    Should Be Equal    ${LIST WITH ESCAPES}[2]    three \\\\\\
    Should Be Equal    ${LIST WITH ESCAPES}[3]    \${non_existing}

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
    Should Be Equal    ${lowercaselist}[0]    Variable name in lower case
    Should Be Equal    ${LOWERCASE LIST}[0]    Variable name in lower case
    Should Be Equal    ${lOWErcasE List}[0]    Variable name in lower case

Variable Names Are Space Insensitive
    Should Be Equal    ${SPACES}    Variable name with spaces
    Should Be Equal    ${ s P a C e s }    Variable name with spaces
    Should Be Equal    ${spaceslist}[0]    Variable name with spaces
    Should Be Equal    ${SP a c es LI st}[0]    Variable name with spaces

Variable Names Are Underscore Insensitive
    Should Be Equal    ${underscores}    Variable name with under scores
    Should Be Equal    ${_U N D_er_Scores__}    Variable name with under scores
    Should Be Equal    ${underscoreslist}[0]    Variable name with under scores
    Should Be Equal    ${ _u_N_de__r _S C ores__ ___L_I_S_T__}[0]    Variable name with under scores

Assign Mark With Scalar variable
    Should Be Equal    ${ASSING MARK}    This syntax works starting from 1.8

Assign Mark With List variable
    Should Be Equal    ${ASSIGN MARK LIST}[0]    This syntax works
    Should Be Equal    ${ASSIGN MARK LIST}[1]    starting
    Should Be Equal    ${ASSIGN MARK LIST}[2]    from
    Should Be Equal    ${ASSIGN MARK LIST}[3]    ${1.8}

Three dots on the same line should be interpreted as string
    Should Be Equal    ${THREE DOTS}    ...
    ${sos} =    Catenate    SEPARATOR=---    @{3DOTS LIST}
    Should Be Equal    ${sos}    ...---...

Scalar catenated from multile values
    Should Be Equal    ${CATENATED}      I am a scalar catenated from many items
    Should Be Equal    ${CATENATED W/ SEP}    I-can-haz-custom-separator

Creating variable using non-existing variable fails
    Variable Should Not Exist    ${NONEX 1}
    Variable Should Not Exist    ${NONEX 2A}
    Variable Should Not Exist    ${NONEX 2B}
    Variable Should Not Exist    ${NONEX 3}
