*** Settings ***
Suite Setup     Remove Files  ${OUTPUTDIR}/*.jp*g
Test Setup      Save Start Time
Test Teardown   Remove Files  ${OUTPUTDIR}/*.jp*g
Resource        screenshot_resource.robot

*** Variables ***
${FIRST_SCREENSHOT}     screenshot_1.jpg
${SECOND_SCREENSHOT}    screenshot_2.jpg

*** Test Cases ***
Screenshot Is Embedded in Log File
    ${path}=    Take Screenshot and Verify    ${FIRST_SCREENSHOT}
    Should Be Equal    ${path}    ${OUTPUTDIR}${/}${FIRST_SCREENSHOT}

Each Screenshot Gets Separate Index
    Take Screenshot and Verify    ${FIRST_SCREENSHOT}
    Take Screenshot and Verify    ${FIRST_SCREENSHOT}    ${SECOND_SCREENSHOT}

Basename May Be Defined
    Repeat Keyword    2    Take Screenshot    foo
    Screenshots Should Exist    ${OUTPUTDIR}    foo_1.jpg    foo_2.jpg

Basename With Extension Turns Off Index Generation
    Repeat Keyword    3    Take Screenshot    xxx.jpg
    Repeat Keyword    2    Take Screenshot    yyy.jpeg
    Screenshots Should Exist  ${OUTPUTDIR}    xxx.jpg    yyy.jpeg

Name as `pathlib.Path`
    Take Screenshot    ${{pathlib.Path('name.jpg')}}
    Screenshots Should Exist    ${OUTPUTDIR}    name.jpg

Screenshot Width Can Be Given
    Take Screenshot    width=300px
    Screenshots Should Exist    ${OUTPUTDIR}    ${FIRST_SCREENSHOT}

Basename With Non-existing Directories Fails
    [Documentation]  FAIL Directory '${OUTPUTDIR}${/}non-existing' where to save the screenshot does not exist
    Take Screenshot    ${OUTPUTDIR}${/}non-existing${/}foo

Without Embedding
    Take Screenshot Without Embedding    no_embed.jpeg

*** Keywords ***
Take Screenshot And Verify
    [Arguments]    @{expected files}
    ${path}=    Take Screenshot
    Screenshots Should Exist    ${OUTPUTDIR}    @{expected files}
    RETURN    ${path}
