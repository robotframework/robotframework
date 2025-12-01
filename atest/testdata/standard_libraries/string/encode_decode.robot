*** Settings ***
Library           String

*** Variables ***
${ASCII: bytes}     Hello, world!
${LATIN1: bytes}    Hyv\xe4
${UTF8: bytes}      Hyv\xc3\xa4

*** Test Cases ***
Encode ASCII String To Bytes
    ${bytes} =    Encode String To Bytes    Hello, world!    UTF-8
    Should Be Equal    ${bytes}    Hello, world!    type=bytes

Encode Non-ASCII String To Bytes
    ${bytes} =    Encode String To Bytes    Hyvä    ISO-8859-1
    Should Be Equal    ${bytes}    Hyv\xe4    type=bytes
    ${bytes} =    Encode String To Bytes    Hyvä    UTF-8    strict
    Should Be Equal    ${bytes}    Hyv\xc3\xa4    type=bytes

Encode Non-ASCII String To Bytes Using Incompatible Encoding
    [Documentation]    FAIL STARTS: UnicodeEncodeError
    Encode String To Bytes    Hyvä    ASCII

Encode Non-ASCII String To Bytes Using Incompatible Encoding And Error Handler
    ${bytes} =    Encode String To Bytes    Hyvä    ASCII    errors=ignore
    Should Be Equal    ${bytes}    Hyv    type=bytes
    ${bytes} =    Encode String To Bytes    Hyvä    ASCII    replace
    Should Be Equal    ${bytes}    Hyv?    type=bytes

Encode bytes
    ${bytes} =    Encode String To Bytes    ${Latin1}    latin-1
    Should Be Equal    ${bytes}    ${Latin1}
    ${bytes} =    Encode String To Bytes    ${UTF8}    latin-1
    Should Be Equal    ${bytes}    ${UTF8}
    ${bytes} =    Encode String To Bytes    ${UTF8}    UTF-8
    Should Be Equal    ${bytes}    ${{b"Hyv\xc3\x83\xc2\xa4"}}

Decode ASCII Bytes To String
    ${string} =    Decode Bytes To String    ${ASCII}    UTF-8
    Should Be Equal    ${string}    Hello, world!

Decode Non-ASCII Bytes To String
    ${string} =    Decode Bytes To String    ${LATIN1}    ISO-8859-1
    Should Be Equal    ${string}    Hyvä
    ${string} =    Decode Bytes To String    ${UTF8}    UTF-8    strict
    Should Be Equal    ${string}    Hyvä

Decode Non-ASCII Bytes To String Using Incompatible Encoding
    [Documentation]    FAIL STARTS: UnicodeDecodeError
    Decode Bytes To String    ${UTF8}    ASCII

Decode Non-ASCII Bytes To String Using Incompatible Encoding And Error Handler
    ${string} =    Decode Bytes To String    ${UTF8}    ASCII    errors=ignore
    Should Be Equal    ${string}    Hyv
    ${string} =    Decode Bytes To String    ${UTF8}    ASCII    replace
    Should Be Equal    ${string}    Hyv\ufffd\ufffd

Decode string
    ${string} =    Decode Bytes To String    hello    ASCII
    Should Be Equal    ${string}    hello
    ${string} =    Decode Bytes To String    hyvä    latin-1
    Should Be Equal    ${string}    hyvä
