*** Settings ***
Variables         resvarfiles/variables.py
Variables         pythonpath_varfile.py    imported by path
Variables         pythonpath_varfile       imported     as module
Variables         package.submodule

*** Variables ***
${DEFINITION IN VARIABLE FILE 1}    ${STRING}
${DEFINITION IN VARIABLE FILE 2}    ${LIST[0]}! ${ONE ITEM[0]}
${DEFINITION IN VARIABLE FILE 3}    ${LIST WITH ESCAPES}
@{DEFINITION IN VARIABLE FILE 4}    @{LIST WITH ESCAPES 2}

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
    Should Be True    ${LIST} == ['Hello','world', '!']
    Should Be Equal    ${LIST[0]}    Hello
    Should Be Equal    ${LIST[1]}    world
    Should Be Equal    ${LIST[2]}    !

Scalar List With Non-Strings
    Should Be True    ${LIST WITH NON STRINGS} == [42, -1.2, True, None]

Scalar List With Escapes
    Test List With Escapes
    ...    ${LIST WITH ESCAPES [0]}    ${LIST WITH ESCAPES [1]}
    ...    ${LIST WITH ESCAPES [2]}    ${LIST WITH ESCAPES [3]}
    ${exp} =    Create List    one \\    two \\\\    three \\\\\\    \${non_existing}
    Should Be Equal    ${LIST WITH ESCAPES}    ${exp}
    # Backslashes are doubled because 'Should Be True' uses 'eval' internally.
    Should Be True    ${LIST WITH ESCAPES} == ['one \\\\', 'two \\\\\\\\', 'three \\\\\\\\\\\\', '\${non_existing}']

Scalar Object
    Should Not Be Equal    ${OBJECT}    dude    Comparing object to string
    Should Be Equal    Hi ${OBJECT}!!    Hi dude!!    Comparing two strings
    Should Be Equal    ${OBJECT.name}    dude
    Should Be Equal    ${OBJECT.name.capitalize()} says hi!    Dude says hi!

List with One Item
    Should Be True    ${ONE ITEM} == ['Hello again?']
    Should Be Equal    ${ONE ITEM}[0]    Hello again?

List With Multiple Items
    Should Be Equal    ${LIST 2}[0]    Hello
    Should Be Equal    ${LIST 2}[1]    again
    Should Be Equal    ${LIST 2}[2]    ?
    Should Be True    ${LIST 2} == ['Hello', 'again', '?']

List With Escapes
    Test List With Escapes    @{LIST WITH ESCAPES}

List With No Items
    Should Be True    ${EMPTY LIST} == []
    ${ret} =    Catenate    @{EMPTY LIST}    @{EMPTY LIST}    only value    @{EMPTY LIST}
    Should Be Equal    ${ret}    only value

List With Objects
    Should Be Equal    ${objects}[0]    Hello world!
    Should Be Equal    ${objects}[1]    ${42}
    Should Be Equal    ${objects}[2]    ${LIST}
    Should Be Equal    ${objects}[3]    ${OBJECT}
    Should Be Equal    -- ${objects} --    -- ['${STRING}', ${INTEGER}, ${LIST}, '${OBJECT}'] --
    Should Be Equal    -- ${objects} --    -- ['Hello world!', 42, ['Hello', 'world', '!'], 'dude'] --

Variable Names Are Case Insensitive
    Should Be Equal    ${lowercase}    Variable name in lower case
    Should Be Equal    ${LOWERCASE}    Variable name in lower case
    Should Be Equal    ${LoWerCAse}    Variable name in lower case
    Should Be Equal    ${lowercase list}[0]    Variable name in lower case
    Should Be Equal    ${LOWERCASE list}[0]    Variable name in lower case
    Should Be Equal    ${lOWErcasE List}[0]    Variable name in lower case

Variable Names Are Underscore Insensitive
    Should Be Equal    ${underscores}    Variable name with under scores
    Should Be Equal    ${_U N D_er_Scores__}    Variable name with under scores
    Should Be Equal    ${underscores list}[0]    Variable name with under scores
    Should Be Equal    ${ _u_N_de__r _S C ores__ _L__ist___}[0]    Variable name with under scores

Variables From Variable Files Can Be Used In Local Variable Table
    Should Be Equal    ${DEFINITION IN VARIABLE FILE 1}    Hello world!
    Should Be Equal    ${DEFINITION IN VARIABLE FILE 2}    Hello! Hello again?
    Test List With Escapes    @{DEFINITION IN VARIABLE FILE 3}
    Test List With Escapes    @{DEFINITION IN VARIABLE FILE 4}

Variable file from PYTHONPATH imported by path
    Should be Equal    ${PYTHONPATH VAR 1}     Varfile found from PYTHONPATH
    Should be Equal    ${PYTHONPATH ARGS 1}    imported by path

Variable file from PYTHONPATH imported as module
    Should be Equal    ${PYTHONPATH VAR 2}     Varfile found from PYTHONPATH
    Should be Equal    ${PYTHONPATH ARGS 2}    imported-as module

Variable file from PYTHONPATH imported as sub module
    Should be Equal    ${VARIABLE IN SUBMODULE}    VALUE IN SUBMODULE

*** Keywords ***
Test List With Escapes
    [Arguments]    ${item1}    ${item2}    ${item3}    ${item4}
    Should Be Equal    ${item1}    one \\
    Should Be Equal    ${item2}    two \\\\
    Should Be Equal    ${item3}    three \\\\\\
    Should Be Equal    ${item4}    \${non_existing}
