*** Settings ***

*** Keywords ***
Keyword Is In Resource File
    Log  hello, resource file

An Other Resource File
    [Arguments]  ${keyword}
    Should Be Equal  ${keyword}  keyword

