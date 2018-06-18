*** Settings ***
Suite Setup     Remove Files  ${OUTPUTDIR}/*.jp*g  ${OUTPUTDIR}/*.png
Test Setup      Save Start Time
Test Teardown   Remove Files  ${OUTPUTDIR}/*.jp*g  ${OUTPUTDIR}/*.png
Resource        screenshot_resource.robot

*** Variables ***
${BASENAME}  ${OUTPUTDIR}${/}screenshot 
${FIRST_SCREENSHOT}  ${BASENAME}_1.jpg
${SECOND_SCREENSHOT}  ${BASENAME}_2.jpg
${FIRST_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo_1.jpg
${SECOND_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo_2.jpg
${PNG_SCREENSHOT}  ${BASENAME}_1.png

*** Test Cases ***
Screenshot Is Embedded in Log File
    ${path}=  Take Screenshot and Verify  jpg  ${FIRST_SCREENSHOT}
    Should Be Equal  ${path}  ${FIRST_SCREENSHOT}

Each Screenshot Gets Separate Index
    Take Screenshot and Verify  jpg  ${FIRST_SCREENSHOT}
    Take Screenshot and Verify  jpg  ${FIRST_SCREENSHOT}  ${SECOND_SCREENSHOT}

Basename May Be Defined
    Repeat Keyword  2  Take Screenshot  foo
    Screenshots Should Exist  ${OUTPUTDIR}  ${FIRST_CUSTOM_SCREENSHOT}  ${SECOND_CUSTOM_SCREENSHOT}

Basename With Extension Turns Off Index Generation
    Repeat Keyword  3  Take Screenshot  xxx.jpg
    Repeat Keyword  2  Take Screenshot  yyy.jpeg
    Screenshots Should Exist  ${OUTPUTDIR}  ${OUTPUTDIR}${/}xxx.jpg  ${OUTPUTDIR}${/}yyy.jpeg

Screenshot Width Can Be Given
    Take Screenshot  width=300px
    Screenshots Should Exist  ${OUTPUTDIR}  ${FIRST_SCREENSHOT}

Basename With Non-existing Directories Fails
    [Documentation]  FAIL Directory '${OUTPUTDIR}${/}non-existing' where to save the screenshot does not exist
    Take Screenshot  ${OUTPUTDIR}${/}non-existing${/}foo

Without Embedding
    Take Screenshot Without Embedding  no_embed.jpeg

Png Screenshot Is Embedded in Log File
    ${path}=  Take Screenshot and Verify  png  ${PNG_SCREENSHOT}
    Should Be Equal  ${path}  ${PNG_SCREENSHOT}

*** Keywords ***
Take Screenshot And Verify  [Arguments]  ${format}  @{expected files}
    ${path}=  Take Screenshot  format=${format}
    Screenshots Should Exist  ${OUTPUTDIR}  @{expected files}
    [Return]  ${path}
