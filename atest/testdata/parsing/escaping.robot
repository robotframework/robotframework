*** Settings ***
Variables         escaping_variables.py

*** Variables ***
${MY SPACE}       \ \
${TWO SPACES}     ${MY SPACE}${MY SPACE}
${FOUR SPACES}    \ \ \ \ \
${PRE SPACES}     \ \ two leading spaces
${POST SPACES}    seven trailing spaces \ \ \ \ \ \ \
${BACKSLASH}      c:\\temp\\new\\
${BACKSLASH 2}    c:\temp\new\
${NEWLINE}        \n
${TABULATOR}      \t
${CARRIAGE}       \r
${NL TAB CR}      \n${NEWLINE}\t${TABULATOR}\r${CARRIAGE}
${NOT VAR}        \${whatever}
${NOT VAR 2}      ${NOT VAR}
@{LIST}           \ \    c:\\temp\\    \n    \${xxx}
${NON STRING}     ${None}

*** Test Cases ***
Spaces In Variable Table
    Should Be Equal    ${MY SPACE}    ${SP}
    Should Be Equal    ${MY SPACE}${MY SPACE}    ${SP}${SP}
    Should Be Equal    ${MY SPACE * 3}    ${SP}${SP}${SP}
    Should Be Equal    ${TWO SPACES}    ${SP}${SP}
    Should Be Equal    ${FOUR SPACES}    ${SP}${SP}${SP}${SP}
    Should Be True    len('${FOUR SPACES}') == 4
    Should Be Equal    "\n${FOUR SPACES}"    "${NL}${SP}${SP}${SP}${SP}"

Leading And Trailing Spaces In Variable Table
    Should Be Equal    ${PRE SPACES}    ${SP}${SP}two leading spaces
    Should Be Equal    ${POST SPACES}    seven trailing spaces${SP*7}
    Should Be Equal    ${POST SPACES}${PRE SPACES}    seven trailing spaces${SP*9}two leading spaces

Backslash In Variable Table
    Should Be Equal    ${BACKSLASH}    c:${BS}temp${BS}new${BS}
    Should Be Equal    ${BACKSLASH}${BS}${BS}    c:${BS}temp${BS}new${BS*3}
    Should Be Equal    ${BACKSLASH}${PRE SPACES}    c:${BS}temp${BS}new${BS}${SP*2}two leading spaces
    Should Be Equal    ${BACKSLASH 2}    c:${TAB}emp${NL}ew

Newline, Tab And Carriage Return In Variable Table
    Should Be Equal    ${NEWLINE}    ${NL}
    Should Be Equal    ${TABULATOR}    ${TAB}
    Should Be Equal    ${CARRIAGE}    ${CR}
    Should Be Equal    ${NL TAB CR}    ${NL*2}${TAB*2}${CR*2}
    Should Be Equal    ${SP}${NEWLINE}    ${SP}${NL}

Escaping Variables In Variable Table
    Should Be Equal    ${NOT VAR}    \${whatever}
    Should Be Equal    ${NOT VAR 2}    \${whatever}
    Should Be Equal    \\${NOT VAR}    \\\${whatever}
    Should Be Equal    \\${NOT VAR 2}    \\\${whatever}
    Should Start With    \${NOT VAR}    \${NOT VAR

Escaping From List Variable In variable Table
    Should Be Equal    ${LIST}[0]    ${SP}
    Should Be Equal    ${LIST}[1]    c:${BS}temp${BS}
    Should Be Equal    ${LIST}[2]    ${NL}
    Should Be Equal    ${LIST}[3]    \${xxx}
    Should Be True    ${LIST} == [' ', 'c:\\\\temp\\\\', '\\n', '$'+'{xxx}']

Non Strings Are Ok In variable Table
    Should Be Equal    ${NON STRING}    ${None}

Remove Spaces Before And After
    Should Be Equal    foo    foo

Remove Extra Spaces between
    Should Be Equal    foo bar    foo bar

Escaping Space
    Should Be Equal    \ \ foo \ \    ${SP*2}foo${SP*2}
    ${x} =    Set Variable    \ \
    Should Be Equal    ${x}    ${SP}
    Should Be Equal    ${x}${x}    ${SP}${SP}
    Should Be Equal    ${x*4}    ${SP}${SP}${SP}${SP}

Backslash
    Should Be Equal    \\    ${BS}
    Should Be Equal    \foo    foo

Newline
    Should Be Equal    \n            ${NL}
    Should Be Equal    \\n           ${BS}n
    Should Be Equal    foo\n\ bar    foo${NL}${SP}bar
    Should Be Equal    foo\\n bar    foo${BS}n${SP}bar

Space After Newline Is parsed
    Should Be Equal    foo\n bar\n zap    foo${NL} bar${NL} zap

Carrriage Return
    Should Be Equal    \r    ${CR}
    Should Be Equal    \\r    ${BS}r

Tabulator
    Should Be Equal    \t    ${TAB}
    Should Be Equal    \\t    ${BS}t

Valid \\x Escape
    Should Be Equal    \x00    ${x00}
    Should Be Equal    \x09\x0A\x0d    \t\n\r
    Should Be Equal    \xe4    ${xE4}
    Should Be Equal    \xFF    ${xFF}
    Should Be Equal    \x50\xf6\x6cj\xE4    Pöljä
    Log    Bytes 0-10: "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A"

Invalid \\x Escape
    Should Be Equal    \x    x
    Should Be Equal    \x+1    x+1
    Should Be Equal    \\x00    ${BS}x00
    Should Be Equal    xx\xxx    xxxxx
    Should Be Equal    \x0    x0

Valid \\u Escape
    Should Be Equal    \u0000    ${x00}
    Should Be Equal    \u00e4    ${xE4}
    Should Be Equal    \u00FF    ${xFF}
    Should Be Equal    \u2603    ${u2603}
    Should Be Equal    \uFfFf    ${uFFFF}
    Should Be Equal    \u0050\u00f6\x6cj\u00E4    Pöljä
    Log    Snowman: \u2603

Invalid \\u Escape
    Should Be Equal    \u    u
    Should Be Equal    \u+123    u+123
    Should Be Equal    \\u1234    ${BS}u1234
    Should Be Equal    uuuu\uuuuu    uuuuuuuuu
    Should Be Equal    \u123    u123

Valid \\U (32bit) Escape
    Should Be Equal    \U00000000    ${x00}
    Should Be Equal    \U000000e4    ${xE4}
    Should Be Equal    \U00002603    ${u2603}
    Should Be Equal    \U00010905    ${U00010905}
    Should Be Equal    \U0010FFFF    ${U0010FFFF}
    Should Be Equal    \U00000050\u00f6\x6cj\U000000E4    Pöljä
    Log    Phoenician letter wau: \U00010905

Invalid \\U (32bit) Escape
    Should Be Equal    \U    U
    Should Be Equal    \U+0001234    U+0001234
    Should Be Equal    \\U00012345    ${BS}U00012345
    Should Be Equal    \UUUUUUUUU    UUUUUUUUU
    Should Be Equal    \U0000123x    U0000123x
    Should Be Equal    \U0000123    U0000123

\\U (32bit) Escape Above Valid Range
    Should Be Equal    \U00110000    U00110000
    Should Be Equal    \U12345678    U12345678
    Should Be Equal    \UffffFFFF    UffffFFFF

Hash
    Should Be Equal    \#    ${HASH}    # This is a comment

Any Character Escaped
    Should Be Equal    \0    0
    Should Be Equal    \a    a
    Should Be Equal    \x    x
    Should Be Equal    \ä    ä

Escaping Variables
    [Documentation]    FAIL Variable '\${foobar}' not found.
    Should Be Equal    \${foo}    $\{foo}
    Should Be Equal    \\${var}    \\\${non_existing}
    Should Be Equal    \${foobar}    ${foobar}

Escaping Variables With User Keywords
    ${ret} =    User Keyword    \${foo}    foo
    Should Be Equal    ${ret}    \${foo}\${foo}
    User keyword 2    \${foo}    {foo}

Pipe
| | Should Be Equal | \| | ${PIPE} |
| | Should Be Equal | \||| | ${PIPE * 3} |

*** Keywords ***
User keyword
    [Arguments]    ${a1}    ${a2}
    Should Contain    ${a1}    ${a2}
    RETURN    ${a1}\${${a2}}

User keyword 2
    [Arguments]    ${a1}    ${a2}
    Should Be Equal    ${a1}    $${a2}
    ${ret} =    User Keyword    ${a1}    ${a2}
    Should Be Equal    ${ret}    ${a1}\${${a2}}
