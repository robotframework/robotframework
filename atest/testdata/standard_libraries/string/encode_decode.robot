*** Settings ***
Library           String
Suite Setup       Create Byte String Variables

*** Variables ***
${ISO-8859-1}     <set by suite setup>
${UTF-8}          <set by suite setup>

*** Test Cases ***
Encode ASCII String To Bytes
    ${bytes} =    Encode String To Bytes    Hello, world!    UTF-8
    Byte Strings Should Be Equal    ${bytes}    Hello, world!

Encode Non-ASCII String To Bytes
    ${bytes} =    Encode String To Bytes    Hyvä    ISO-8859-1
    Byte Strings Should Be Equal    ${bytes}    Hyv\\xe4
    ${bytes} =    Encode String To Bytes    Hyvä    UTF-8    strict
    Byte Strings Should Be Equal    ${bytes}    Hyv\\xc3\\xa4

Encode Non-ASCII String To Bytes Using Incompatible Encoding
    [Documentation]    FAIL STARTS: UnicodeEncodeError
    Encode String To Bytes    Hyvä    ASCII

Encode Non-ASCII String To Bytes Using Incompatible Encoding And Error Handler
    ${bytes} =    Encode String To Bytes    Hyvä    ASCII    errors=ignore
    Byte Strings Should Be Equal    ${bytes}    Hyv
    ${bytes} =    Encode String To Bytes    Hyvä    ASCII    replace
    Byte Strings Should Be Equal    ${bytes}    Hyv?

Decode ASCII Bytes To String
    ${string} =    Decode Bytes To String    ${ASCII}    UTF-8
    Should Be Equal    ${string}    Hello, world!

Decode Non-ASCII Bytes To String
    ${string} =    Decode Bytes To String    ${ISO-8859-1}    ISO-8859-1
    Should Be Equal    ${string}    Hyvä
    ${string} =    Decode Bytes To String    ${UTF-8}    UTF-8    strict
    Should Be Equal    ${string}    Hyvä

Decode Non-ASCII Bytes To String Using Incompatible Encoding
    [Documentation]    FAIL STARTS: UnicodeDecodeError
    Decode Bytes To String    ${UTF-8}    ASCII

Decode Non-ASCII Bytes To String Using Incompatible Encoding And Error Handler
    ${string} =    Decode Bytes To String    ${UTF-8}    ASCII    errors=ignore
    Should Be Equal    ${string}    Hyv
    ${string} =    Decode Bytes To String    ${UTF-8}    ASCII    replace
    # Cannot compare exactly because replacement character is different in IronPython than elsewhere
    Should Match    ${string}    Hyv??

Decoding String Fails
    [Documentation]    FAIL TypeError: Can not decode strings on Python 3.
    Decode Bytes To String    hello    ASCII

*** Keywords ***
Create Byte String Variables
    ${ASCII}=    Evaluate    b"Hello, world!"
    ${ISO-8859-1} =    Evaluate    b"Hyv\\xe4"
    ${UTF-8} =    Evaluate    b"Hyv\\xc3\\xa4"
    Set Suite Variable    ${ASCII}
    Set Suite Variable    ${ISO-8859-1}
    Set Suite Variable    ${UTF-8}

Byte Strings Should Be Equal
    [Arguments]    ${bytes}    ${expected}
    Should Be Byte String    ${bytes}
    ${expected} =    Evaluate    b"${expected}"
    Should Be Equal    ${bytes}    ${expected}
