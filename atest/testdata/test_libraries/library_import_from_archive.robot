*** Setting ***
Library           ZipLib
Library           org.robotframework.JarLib

*** Test Case ***
Python Library From a Zip File
    ${ret} =    Kw From Zip    ${4}
    Should Be Equal    ${ret}    ${8}

Java Library From a Jar File
    Kw From Jar    Hello
