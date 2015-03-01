*** Settings ***
Library           String
Suite Setup       Create Bytes and String Variables

*** Variables ***
${BYTES}          <set by suite setup>

*** Test Cases ***
Should Be String Positive
    Should be String    Robot
    Should be String    ${EMPTY}
    Should be String    ${STRING}

Should Be String Negative
    [Template]     Run Keyword And Expect Error
    '0' is not a string.    Should be string    ${0}
    My error    Should be string    ${TRUE}    My error

Should Not Be String Positive
    Should Not Be String    ${0}
    Should Not Be String    ${TRUE}

Should Not Be String Negative
    [Template]    Run Keyword And Expect Error
    '${STRING}' is a string.    Should not be string    ${STRING}
    My error message    Should not be string    Hello    My error message

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
    Should Be Lowercase    ${STRING.lower()}

Should Be Lowercase Negative
    [Template]    Run Keyword And Expect Error
    '${STRING}' is not lowercase.    Should Be Lowercase    ${STRING}
    My error    Should Be Lowercase    UP!    My error

Should Be Uppercase Positive
    Should Be Uppercase    FOO BAR
    Should Be Uppercase    ${STRING.upper()}

Should Be Uppercase Negative
    [Template]    Run Keyword And Expect Error
    '${STRING}' is not uppercase.    Should Be Uppercase    ${STRING}
    Custom error    Should Be Uppercase    low...    Custom error

Should Be Titlecase Positive
    Should Be Titlecase    Foo Bar!
    Should Be Titlecase    ${STRING}

Should Be Titlecase Negative
    [Template]    Run Keyword And Expect Error
    '${STRING.lower()}' is not titlecase.    Should Be Titlecase    ${STRING.lower()}
    Special error    Should Be Titlecase    all low    Special error

*** Keywords ***
Create Bytes and String Variables
    ${STRING} =    Evaluate    "Hyv\\xe4"
    Set Suite Variable    ${STRING}
    ${BYTES} =    Convert To Bytes    ${STRING}
    Set Suite Variable    ${BYTES}
