*** Setting ***
Documentation    Testing different ways to write "Setting(s)".

*** Comment ***
This table is accepted and data here ignored.

***SET TINGS***
Default Tags    Settings
Library         OperatingSystem

***Variable***
${VARIABLE}  Variable

***VAR I A BLES***
${VARIABLES}  Variables

***Test Case***
Test Case
    Log  ${VARIABLE}
    Keyword

***COMMENTS***
Comment tables are case (and space) insensitive like any other table and
both singular and plural formats are fine.
***COMMENTS***

***TestCases***
Test Cases
    Log  ${VARIABLES}

Comment tables exist
    ${content} =    Get File    ${CURDIR}/table_names.robot
    Should Contain    ${content}    \n*** Comment ***\n

* * * K e y w o r d * * *
Keyword
    Keywords

*keywords
Keywords
    Log    "Keywords" was executed
