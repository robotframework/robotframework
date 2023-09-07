*** Settings ***
Documentation    Testing different ways to write "Settings".

*** Comments ***
This table is accepted and data here ignored.

***SETTINGS***
Test Tags       Settings
Library         OperatingSystem

***Variables***
${V1}           Variables

*** VARIABLES ***
${V2}           VARIABLES

***Test Cases***
Test Case
    Log    ${V1}
    Keyword

***COMMENTS***
Comment headers are case insensitive like all other headers.
***COMMENTS***

*** Test CASES ***
Test Cases
    Log    ${V2}

Comment section exist
    ${content} =    Get File    ${CURDIR}/table_names.robot
    Should Contain    ${content}    \n*** Comments ***\n
    Should Contain    ${content}    \n***COMMENTS***\n

*** Keywords ***
Keyword
    Keywords

*keywords
Keywords
    Log    "Keywords" was executed

* * * K e y w o r d * * *
Keyword
    Fail    Should not be executed (or even parsed)

*** Setting ***
Metadata     Singular headers    Deprecated
*** variable ***
${V3}        Deprecated
*** TEST CASE ***
Singular headers are deprecated
    Singular headers are deprecated
*keyword
Singular headers are deprecated
    Should Be Equal    ${V3}    Deprecated
*** Comment ***
Yes, singular headers are deprecated.
