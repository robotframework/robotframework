*** Asetukset ***
Dokumentaatio      Suite documentation.
Metadata           Metadata    Value
Setin Alustus      Suite Setup
Setin Purku        Suite Teardown
Testin Alustus     Test Setup
Testin Purku       Test Teardown
Testin Malli       Test Template
Testin Tagit       forced tag
Oletus Tagit       default tag
Testin Aikaraja    1 minute
Kirjasto           OperatingSystem
Resurssi           finnish.resource
Muuttujat          variables.py

*** Muuttujat ***
${VARIABLE}        variable value

*** Testit ***
Test without settings
    Nothing to see here

Test with settings
    [Dokumentaatio]    Test documentation.
    [Tagit]            own tag
    [Alustus]          NONE
    [Purku]            NONE
    [Malli]            NONE
    [Aikaraja]         NONE
    ${result} =        Keyword      ${VARIABLE}
    Should Be Equal    ${result}    To be deprecated

*** Avainsanat ***
Suite Setup
    Directory Should Exist    ${CURDIR}

Suite Teardown
    Keyword In Resource

Test Setup
    Should Be Equal    ${VARIABLE}         variable value
    Should Be Equal    ${RESOURCE FILE}    variable in resource file
    Should Be Equal    ${VARIABLE FILE}    variable in variable file

Test Teardown
    No Operation

Test Template
    [Argumentit]    ${message}
    Log    ${message}

Keyword
    [Dokumentaatio]    Keyword documentation.
    [Argumentit]       ${arg}
    [Tagit]            kw tag
    [Aikaraja]         1h
    Should Be Equal    ${arg}    ${VARIABLE}
    [Purku]            No Operation
    [Paluuarvo]        To be deprecated

*** Kommentit ***
Ignored comments.
