*** Variables ***
${STRING}               Hello world!
${INTEGER}              ${42}
${FLOAT}                ${-1.2}
${BOOLEAN}              ${True}
${NONE VALUE}           ${None}
${ESCAPES}              one \\ two \\\\ \${non_existing}
${SPACE ESC}            \ 1 leading, \ 2 middle, 3 trailing \ \ \
${NO VALUE}             ${EMPTY}
@{ONE ITEM}             Hello again?
@{LIST}                 Hello    again    ?
@{LIST WITH ESCAPES}    one \\    two \\\\    three \\\\\\    \${non_existing}
@{LIST CREATED FROM LIST WITH ESCAPES}    @{LIST WITH ESCAPES}
@{SPACE ESC LIST}       \ lead    trail \    \ \ 2 \ \    \ \ \ 3 \ \ \
@{EMPTY LIST}
${lowercase}            Variable name in lower case
@{lowercaselist}        Variable name in lower case
${S P a c e s }         Variable name with spaces
@{s P a c es li S T}    Variable name with spaces
${UNDER_scores}         Variable name with under scores
@{_u_n_d_e_r___s_c_o_r_e_s__li_ST}    Variable name with under scores
${ASSING MARK} =        This syntax works starting from 1.8
@{ASSIGN MARK LIST}=    This syntax works    starting    from    ${1.8}
${THREE DOTS}           ...
@{3DOTS LIST}           ...   ...
${CATENATED}            By    default    values    are    joined    with    a    space
${SEPARATOR VALUE}      SEPARATOR=-    Special    SEPARATOR    marker    as    ${1}    st    value
${SEPARATOR OPTION}     Explicit    separator    option    works    since    RF    ${7.0}    separator=-
${BOTH SEPARATORS}      SEPARATOR=marker    has    lower    precedence    than    option    separator=:
${VAR}                  existing
${BASED ON ${VAR}}      Supported since 7.0
${BASED ON ${BAD}}      Ooop!
Invalid Name            Decoration missing
${}                     Body missing
${not                   closed
${not}[ok]              This is variable but not valid assign
${NONEX 1}              Creating variable based on ${NON EXISTING} variable fails.
${NONEX 2A}             This ${NON EX} is used for creating another variable.
${NONEX 2B}             ${NONEX 2A}
${NONEX 3}              This ${NON EXISTING VARIABLE} is used in imports.

*** Settings ***
Resource                ${NONEX 3}
Library                 ${NONEX 3}

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
    Should Be Equal    ${SPACE ESC}    ${SPACE}1 leading,${SPACE*2}2 middle, 3 trailing${SPACE*3}

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
    Should Be Equal    ${SPACE ESC LIST}[0]    ${SPACE}lead
    Should Be Equal    ${SPACE ESC LIST}[1]    trail${SPACE}
    Should Be Equal    ${SPACE ESC LIST}[2]    ${SPACE*2}2${SPACE*2}
    Should Be Equal    ${SPACE ESC LIST}[3]    ${SPACE*3}3${SPACE*3}

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
    Should Be Equal    ${LOWERCASELIST}[0]    Variable name in lower case
    Should Be Equal    ${lOWErcasE List}[0]    Variable name in lower case

Variable Names Are Space Insensitive
    Should Be Equal    ${SPACES}    Variable name with spaces
    Should Be Equal    ${ s P a C e s }    Variable name with spaces
    Should Be Equal    ${spaceslist}[0]    Variable name with spaces
    Should Be Equal    ${SP a c es L I S t}[0]    Variable name with spaces

Variable Names Are Underscore Insensitive
    Should Be Equal    ${underscores}    Variable name with under scores
    Should Be Equal    ${_U N D_er_Scores__}    Variable name with under scores
    Should Be Equal    ${underscoreslist}[0]    Variable name with under scores
    Should Be Equal    ${ _u_N_de__r _S C ores__ _L__ISt__}[0]    Variable name with under scores

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

Scalar catenated from multiple values
    Should Be Equal    ${CATENATED}           By default values are joined with a space

Scalar catenated from multiple values with 'SEPARATOR' marker
    Should Be Equal    ${SEPARATOR VALUE}     Special-SEPARATOR-marker-as-1-st-value

Scalar catenated from multiple values with 'separator' option
    Should Be Equal    ${SEPARATOR OPTION}    Explicit-separator-option-works-since-RF-7.0
    Should Be Equal    ${BOTH SEPARATORS}     SEPARATOR=marker:has:lower:precedence:than:option

Named based on another variable
    Should Be Equal    ${BASED ON EXISTING}    Supported since 7.0

Creating variable using non-existing variable fails
    Variable Should Not Exist    ${NONEX 1}
    Variable Should Not Exist    ${NONEX 2A}
    Variable Should Not Exist    ${NONEX 2B}
    Variable Should Not Exist    ${NONEX 3}
