language: fi

*** Asetukset ***
Nimi                Custom name
Dokumentaatio       Suite documentation.
Metatiedot          Metadata    Value
Setin Alustus       Suite Setup
Setin Alasajo       Suite Teardown
Testin Alustus      Test Setup
Testin Alasajo      Test Teardown
Testin Malli        Test Template
Testin Aikaraja     1 minute
Testin Tagit        test    tags
Avainsanan Tagit    keyword    tags
Kirjasto            OperatingSystem
Resurssi            ../finnish/resource.resource
Muuttujat           ../../variables.py

*** Muuttujat ***
${VARIABLE}         variable value

*** Testit ***
Test without settings
    Nothing to see here

Test with settings
    [Dokumentaatio]    Test documentation.
    [Tagit]            own tag
    [Alustus]          NONE
    [Alasajo]          NONE
    [Malli]            NONE
    [Aikaraja]         NONE
    Keyword            ${VARIABLE}

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
    [Tagit]            own tag
    [Aikaraja]         1h
    [Alustus]          Log    Hello, setup!
    Should Be Equal    ${arg}    ${VARIABLE}
    [Alasajo]          No Operation

*** Kommentit ***
Ignored comments.
