*** Settings ***
Library           String

*** Variables ***
${BYTES: bytes}   Hello
@{EXCLUDES}       a    an    the    to    is

*** Test Cases ***
Should Be String Positive
    Should be String    Robot
    Should be String    ${EMPTY}

Should Be String Negative
    [Template]     Run Keyword And Expect Error
    b'${BYTES}' is bytes, not a string.    Should Be String    ${BYTES}
    0 is integer, not a string.            Should Be String    ${0}
    My error                               Should Be String    ${TRUE}    My error

Should Not Be String Positive
    Should Not Be String    ${BYTES}
    Should Not Be String    ${0}
    Should Not Be String    ${TRUE}

Should Not Be String Negative
    [Template]     Run Keyword And Expect Error
    'Two\\nlines' is a string.    Should not be string    Two\nlines
    My error message              Should not be string    Hello    My error message

Should Be Unicode String Positive
    Should be Unicode String    Robot

Should Be Unicode String Negative
    [Template]     Run Keyword And Expect Error
    b'${BYTES}' is bytes, not a string.    Should Be Unicode String    ${BYTES}
    My error                               Should Be Unicode String    ${0}    My error

Should Be Byte String Positive
    Should be Byte String    ${BYTES}

Should Be Byte String Negative
    [Template]     Run Keyword And Expect Error
    'Hyvä' is not a byte string.    Should Be Byte String    Hyvä
    My error                        Should Be Byte String    ${0}    My error

Should Be Lower Case Positive
    Should Be Lower Case    foo bar
    Should Be Lower Case    ${BYTES.lower()}

Should Be Lower Case Negative
    [Template]    Run Keyword And Expect Error
    My error                          Should Be Lower Case    UP!    My error
    b'${BYTES}' is not lower case.    Should Be Lower Case    ${BYTES}

Should Be Upper Case Positive
    Should Be Upper Case    FOO BAR
    Should Be Upper Case    ${BYTES.upper()}

Should Be Upper Case Negative
    [Template]    Run Keyword And Expect Error
    b'${BYTES}' is not upper case.    Should Be Upper Case    ${BYTES}
    Custom error                      Should Be Upper Case    low...    Custom error

Should Be Title Case Positive
    Should Be Title Case    Foo Bar!
    Should Be Title Case    Abcd
    Should Be Title Case    Äiti
    Should Be Title Case    XML
    Should Be Title Case    jUnit
    Should Be Title Case    3.14
    Should Be Title Case    ----
    Should Be Title Case    3Tm
    Should Be Title Case    \u2603
    Should Be Title Case    \u2603Snowman
    Should Be Title Case    Hello World
    Should Be Title Case    Don't Title T
    Should Be Title Case    'Do' Title "These"
    Should be Title Case    I Don't Have iPhone X11 & It's OK
    Should be Title Case    They're Bill's Friends From The UK
    Should be Title Case    Ääliö Älä Lyö, Ööliä Läikkyy!
    Should be Title Case    ${{b"Hyv\xe4 Esimerkki!"}}

Should Be Title Case Negative
    [Template]    Run Keyword And Expect Error
    'low' is not title case.     Should Be Title Case    low
    Custom error                 Should Be Title Case    low    Custom error
    b'low' is not title case.    Should Be Title Case    ${{b"low"}}

Should Be Title Case With Excludes
    [Template]    Test Title Case
    This is an Example    None   is, an
    This is an Example    None   ${EXCLUDES}
    äiti Ei Ole Iso       exclude=äiti
    Isä on Iso            exclude=äiti,isä,on
    They're Bill's Friends From the UK
    ...                   exclude=${EXCLUDES}
    This Is none          exclude=none
    ${{b"This is OK"}}    exclude=${{b"is, OK"}}
    ${{b"This is OK"}}    exclude=OK, is
    ${{b"This is OK"}}    exclude=${{[b"is", "OK"]}}

Should Be Title Case With Regex Excludes
    [Template]    Test Title Case
    A, B, And C.          exclude=a, b, c
    a, b, And c.          exclude=(a|b|c).
    a, b, And c.          exclude=${{["(a|b|c)[.,]?"]}}
    Full Match Only!      exclude=.
    full Match Only!      exclude=....
    ${{b"This is OK"}}    exclude=${{b".."}}
    ${{b"This is OK"}}    exclude=..

*** Keywords ***
Test title case
    [Arguments]    ${string}    @{args}    &{kwargs}
    Should Be Title Case    ${string}   @{args}    &{kwargs}
