*** Setting ***
Documentation    Testing different ways to write "Setting(s)".

*** Comment ***
This table is accepted and data here ignored.

***SETTINGS***
Default Tags    Settings
Library         OperatingSystem

***Variable***
${VARIABLE}  Variable

*** VARIABLES ***
${VARIABLES}  Variables

***Test Case***
Test Case
    Log  ${VARIABLE}
    Keyword

***COMMENTS***
Comment tables are case (and space) insensitive like any other table and
both singular and plural formats are fine.
***COMMENTS***

*** Test Cases ***
Test Cases
    Log  ${VARIABLES}

Comment tables exist
    ${content} =    Get File    ${CURDIR}/table_names.robot
    Should Contain    ${content}    \n*** Comment ***\n

*** Keyword ***
Keyword
    Keywords

*keywords
Keywords
    Log    "Keywords" was executed

* * * K e y w o r d * * *
Keyword
    Fail    Should not be executed (or even parsed)
