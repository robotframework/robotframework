*** Setting ***
Library           ZipLib

*** Test Case ***
Python Library From a Zip File
    ${ret} =    Kw From Zip    ${4}
    Should Be Equal    ${ret}    ${8}
