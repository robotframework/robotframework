*** Settings ***
Library           ZipLib

*** Test Cases ***
Python Library From a Zip File
    ${ret} =    Kw From Zip    ${4}
    Should Be Equal    ${ret}    ${8}
