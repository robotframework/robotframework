*** Settings ***
Suite Setup     Remove Files  ${OUTPUTDIR}/*.jp*g  ${OUTPUTDIR}/*.png
Test Setup	Save Start Time
Test Teardown   Remove Files  ${OUTPUTDIR}/*.jp*g  ${OUTPUTDIR}/*.png
Resource        screenshot_resource.robot

*** Variables ***
${BASENAME}  ${OUTPUTDIR}${/}screenshot 
${FIRST_SCREENSHOT}  ${BASENAME}_1.jpg
${SECOND_SCREENSHOT}  ${BASENAME}_2.jpg
${FIRST_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo_1.jpg
${SECOND_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo_2.jpg
${PNG_SCREENSHOT}  ${BASENAME}_1.png
${PNG_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo.png
${JPEG_CUSTOM_SCREENSHOT}  ${OUTPUTDIR}${/}foo_3,jpg
${PNG_FORMAT}  png
${JPEG_FORMAT}  jpg

*** Test Cases ***
Screenshot Is Embedded in Log File
    ${path}=  Take Screenshot and Verify  ${FIRST_SCREENSHOT} 
    Should Be Equal  ${path}  ${FIRST_SCREENSHOT}

Each Screenshot Gets Separate Index
    Take Screenshot and Verify  ${FIRST_SCREENSHOT} 
    Take Screenshot and Verify  ${FIRST_SCREENSHOT}  ${SECOND_SCREENSHOT} 

Basename May Be Defined
    Repeat Keyword  2  Take Screenshot  foo
    Screenshots Should Exist  ${OUTPUTDIR}  ${FIRST_CUSTOM_SCREENSHOT}  ${SECOND_CUSTOM_SCREENSHOT}

Screenshot With Png Extension
    Take Screenshot  image_format=png
    Screenshots Should Exist  ${OUTPUTDIR}  ${PNG_SCREENSHOT}

Png Screenshot Quality
    Compare Size  ${PNG_CUSTOM_SCREENSHOT}  ${PNG_FORMAT}

Jpg Screenshot Quality
    Compare Size  ${JPEG_CUSTOM_SCREENSHOT}  ${JPEG_FORMAT}

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


*** Keywords ***
Take Screenshot And Verify  [Arguments]  @{expected files}
    ${path}=  Take Screenshot
    Screenshots Should Exist  ${OUTPUTDIR}  @{expected files}
    [Return]  ${path}

Compare Size 
    [Arguments]  ${screenshot_name}  ${image_format}
    Take Screenshot  ${screenshot_name}  ${screenshot_format}  quality=100
    ${first}=  Get File Size  ${screenshot_name}
    Take Screenshot  ${screenshot_name}  ${screenshot_format}  quality=1
    ${second}=  Get File Size  ${screenshot_name}
    ${result}=  Evaluate  ${second} * 100 / ${first}
    Should Be True  ${result} < 30
