*** Settings ***
Suite Setup     Remove Files  ${OUTPUTDIR}/*.jp*g    ${OUTPUTDIR}/*.png    ${OUTPUTDIR}/*.tiff    ${OUTPUTDIR}/*.bmp
Test Setup      Save Start Time
Test Teardown   Remove Files  ${OUTPUTDIR}/*.jp*g    ${OUTPUTDIR}/*.png    ${OUTPUTDIR}/*.tiff    ${OUTPUTDIR}/*.bmp
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

Basename May Be Defined With Screenshot Format Of PNG
    Repeat Keyword    2    Take Screenshot    foo    img_format=png
    Screenshots Should Exist    ${OUTPUTDIR}    foo_1.png    foo_2.png    format=png

Basename May Be Defined With Screenshot Format Of TIFF
    Repeat Keyword    2    Take Screenshot    foo    img_format=tiff
    Screenshots Should Exist    ${OUTPUTDIR}    foo_1.tiff    foo_2.tiff    format=tiff

Basename With Extension Turns Off Index Generation
    Repeat Keyword    3    Take Screenshot    xxx.jpg    img_format=jpg
    Repeat Keyword    2    Take Screenshot    yyy.jpeg    img_format=jpg
    Screenshots Should Exist  ${OUTPUTDIR}    xxx.jpg    yyy.jpeg    format=jpg
    Repeat Keyword    3    Take Screenshot    xxx.png    img_format=png
    Screenshots Should Exist  ${OUTPUTDIR}    xxx.png    format=png
    Repeat Keyword    3    Take Screenshot    xxx.bmp    img_format=bmp
    Screenshots Should Exist  ${OUTPUTDIR}    xxx.bmp    format=bmp

Name as `pathlib.Path`
    Take Screenshot    ${{pathlib.Path('name.jpg')}}
    Screenshots Should Exist    ${OUTPUTDIR}    name.jpg

Name as `pathlib.Path` - Format PNG
    Take Screenshot    ${{pathlib.Path('name.png')}}    img_format=png
    Screenshots Should Exist    ${OUTPUTDIR}    name.png    format=png

Name as `pathlib.Path` - Format TIFF
    Take Screenshot    ${{pathlib.Path('name.tiff')}}    img_format=tiff
    Screenshots Should Exist    ${OUTPUTDIR}    name.tiff    format=tiff

Screenshot Width Can Be Given
    Take Screenshot    width=300px
    Screenshots Should Exist    ${OUTPUTDIR}    ${FIRST_SCREENSHOT}

Screenshot Width Can Be Given For PNG
    Take Screenshot    foo.png    width=300px    img_format=png
    Screenshots Should Exist    ${OUTPUTDIR}    foo.png    format=png

Screenshot Width Can Be Given For BMP
    Take Screenshot    foo.bmp    width=300px    img_format=bmp
    Screenshots Should Exist    ${OUTPUTDIR}    foo.bmp    format=bmp

Basename With Non-existing Directories Fails
    [Documentation]  FAIL Directory '${/}non-existing' where to save the screenshot does not exist
    Take Screenshot    ${/}non-existing${/}foo

Without Embedding
    Take Screenshot Without Embedding    no_embed.jpeg

Take Screenshot Without Embedding For PNG
    Take Screenshot Without Embedding    no_embed.png    img_format=png

Take Screenshot Without Embedding for TIFF
    Take Screenshot Without Embedding    no_embed.tiff    img_format=tiff

*** Keywords ***
Take Screenshot And Verify
    [Arguments]    @{expected files}
    ${path}=    Take Screenshot
    Screenshots Should Exist    ${OUTPUTDIR}    @{expected files}
    RETURN    ${path}
