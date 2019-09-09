*** Settings ***
Library           MyLibrary    argument    WITH NAME    My Alias    # My library comment
Variables         MyVariables    args    args 2    args 3    args 4    args 5    args 6
...               args 7    args 8    args 9    args 10    args 11    args 12
Resource          MyResource args that are part of the name

*** Variables ***
# standalone      comment
MyVar             val1    val2    val3    val4    val5    val6    val7
...               val8    val9    val10    # var comment
# standalone

*** Test Cases ***
My Test Case
    [Documentation]    This is a long comment that spans several columns
    My TC Step 1    my step arg    # step 1 comment
    My TC Step 2    my step 2 arg    second \ arg    # step 2 comment
    [Teardown]    1 minute    args

Another Test
    Log Many    Non-ASCII: ääöö§§    ${CURDIR}

*** Keywords ***
My Keyword
    [Documentation]    Documentation    # Comment for doc
    [Tags]    keyword    tags
    # Comment row
    # Comment row 2
    My Step 1    args    args 2    args 3    args 4    args 5    args 6
    ...    args 7    args 8    args 9    # step 1 comment
    FOR    ${param1}    ${param2}    IN    ${data 1}    ${data 2}    ${data 3}
    ...    ${data 4}    ${data 5}    ${data 6}    # FOR comment
        Loop Step    args    args 2    args 3    args 4    args 5
        ...    args 6    args 7    args 8    args 9    # loop step comment
        Loop Step 2
    END
    My Step 2    my step 2 arg    second arg    # step 2 comment
    [Return]    args 1    args 2
