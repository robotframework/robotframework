*** Settings ***
Library           String
Suite Setup       Create Byte String Variables

*** Variables ***
${BYTES}          <set by suite setup>

*** Test Cases ***
Should Be String Positive
    Should be String    Robot
    Should be String    ${EMPTY}

Bytes are strings in python 2
    Should be String    ${BYTES}
    Run keyword and expect error    '${BYTES}' is a string.    Should not be string    ${BYTES}

Bytes are not strings in python 3 and ironpython
    Run Keyword And Expect Error   '${BYTES}' is not a string.    Should Be String    ${BYTES}
    Should not be string    ${BYTES}

Should Be String Negative
    [Template]     Run Keyword And Expect Error
    '0' is not a string.    Should be string    ${0}
    My error    Should be string    ${TRUE}    My error

Should Not Be String Positive
    Should Not Be String    ${0}
    Should Not Be String    ${TRUE}

Should Not Be String Negative
    Run Keyword And Expect Error    My error message    Should not be string    Hello    My error message

Should Be Unicode String Positive
    Should be Unicode String    Robot

Should Be Unicode String Negative
    [Template]     Run Keyword And Expect Error
    '${BYTES}' is not a Unicode string.    Should Be Unicode String    ${BYTES}
    My error    Should Be Unicode String    ${0}    My error

Should Be Byte String Positive
    Should be Byte String    ${BYTES}

Should Be Byte String Negative
    [Template]     Run Keyword And Expect Error
    'Hyvä' is not a byte string.    Should Be Byte String    Hyvä
    My error    Should Be Byte String    ${0}    My error

Should Be Lowercase Positive
    Should Be Lowercase    foo bar
    Should Be Lowercase    ${BYTES.lower()}

Should Be Lowercase Negative
    [Template]    Run Keyword And Expect Error
    '${BYTES}' is not lowercase.    Should Be Lowercase    ${BYTES}
    My error    Should Be Lowercase    UP!    My error

Should Be Uppercase Positive
    Should Be Uppercase    FOO BAR
    Should Be Uppercase    ${BYTES.upper()}

Should Be Uppercase Negative
    [Template]    Run Keyword And Expect Error
    '${BYTES}' is not uppercase.    Should Be Uppercase    ${BYTES}
    Custom error    Should Be Uppercase    low...    Custom error

Should Be Titlecase Positive
    Should Be Titlecase    Foo Bar!
    Should Be Titlecase    ${BYTES}

Should Be Titlecase Negative
    [Template]    Run Keyword And Expect Error
    '${BYTES.lower()}' is not titlecase.    Should Be Titlecase    ${BYTES.lower()}
    Special error    Should Be Titlecase    all low    Special error

*** Keywords ***
Create Byte String Variables
    ${BYTES} =    Evaluate    b"Hyv\\xe4"
    Set Suite Variable    ${BYTES}
