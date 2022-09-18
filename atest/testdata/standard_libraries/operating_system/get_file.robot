*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Base Test Directory
Resource          os_resource.robot
Library           String

*** Variables ***
${SYSTEM_ENCODING}          ASCII    # Should be overridden from CLI
${CONSOLE_ENCODING}         ASCII    # Should be overridden from CLI
${UTF-8 FILE}               ${CURDIR}${/}files${/}utf-8.txt
${ASCII FILE}               ${CURDIR}${/}files${/}ascii.txt
${LATIN-1 FILE}             ${CURDIR}${/}files${/}latin-1.txt
${LATIN-1 LONG FILE}        ${CURDIR}${/}files${/}latin-1_multiple_rows.txt
${UTF-8 LONG FILE}          ${CURDIR}${/}files${/}utf-8_multiple_rows.txt
${UTF-16 LE FILE}           ${CURDIR}${/}files${/}utf-16LE.txt       # Little Endian
${UTF-16 BE FILE}           ${CURDIR}${/}files${/}utf-16BE.txt       # Big Endian
${UTF-16 LE W/ BOM FILE}    ${CURDIR}${/}files${/}utf-16LEBOM.txt    # Little Endian with Byte Order Marker
${UTF-16 BE W/ BOM FILE}    ${CURDIR}${/}files${/}utf-16BEBOM.txt    # Big Endian with BOM
${UTF-8 WINDOWS FILE}       ${CURDIR}${/}files${/}utf-8_windows_line_endings.txt
${RESULT}                   Hyvää üötä

*** Test Cases ***
Get File
    Create File    ${TESTFILE}    hello world\nwith two lines
    ${file} =    Get File    ${TESTFILE}
    Should Be Equal    ${file}    hello world\nwith two lines
    ${file} =    Get File    ${TESTFILE}    ascii
    Should Be Equal    ${file}    hello world\nwith two lines

Get File With Non-ASCII Name
    Create File    ${NON ASCII}    content
    ${file} =    Get File    ${NON ASCII}
    Should Be Equal    ${file}    content

Get File With Space In Name
    Create File    ${WITH SPACE}    content
    ${file} =    Get File    ${WITH SPACE}
    Should Be Equal    ${file}    content

Get Utf-8 File
    ${file} =    Get File    ${UTF-8 FILE}
    Should Be Equal    ${file}    ${RESULT}

Get Ascii File With Default Encoding
    ${file} =    Get File    ${ASCII FILE}
    Should Be Equal    ${file}    Hyvaa yota

Get Latin-1 With Default Encoding
    [Documentation]    FAIL REGEXP: (UnicodeDecodeError|UnicodeError)(: .*)?
    Get File    ${LATIN-1 FILE}

Get file with system encoding
    Create File    ${TEST FILE}    ${RESULT}    encoding=${SYSTEM_ENCODING}
    ${file} =    Get file    ${TEST FILE}    encoding=SYStem
    Should Be Equal    ${file}    ${RESULT}

Get file with console encoding
    Create File    ${TEST FILE}    ${RESULT}     encoding=${CONSOLE_ENCODING}
    ${file} =    Get file    ${TEST FILE}    encoding=COnsoLE
    Should Be Equal    ${file}    ${RESULT}

Get Latin-1 With Latin-1 Encoding
    ${file} =    Get File    ${LATIN-1 FILE}    Latin-1
    Should Be Equal    ${file}    ${result}

Get Utf-16 File with Default Encoding
    [Documentation]    FAIL REGEXP: (UnicodeDecodeError|UnicodeError)(: .*)?
    ${file}=    Get File    ${UTF-16LEfile}

Get File with 'ignore' Error Handler
    [Template]    Verify Get File with error handler
    ${UTF-16 BE FILE}    ignore    \x00H\x00y\x00v\x00\x00\x00 \x00\x00\x00t\x00\x00\n\x00f\x00\x00\x00 \x00b\x00a\x00r
    ${LATIN-1 FILE}    ignore    Hyv t

Get File with 'replace' Error Handler
    [Template]    Verify Get File with error handler
    ${UTF-16 BE FILE}    replace    \x00H\x00y\x00v\x00\ufffd\x00\ufffd\x00 \x00\ufffd\x00\ufffd\x00t\x00\ufffd\x00\n\x00f\x00\ufffd\x00\ufffd\x00 \x00b\x00a\x00r
    ${LATIN-1 FILE}    replace    Hyv\ufffd\ufffd \ufffd\ufffdt\ufffd

Get file converts CRLF to LF
    Create Binary File    ${TESTFILE}    1\r\n2\r\n
    ${file}=    Get File    ${TESTFILE}
    Should Be Equal    ${file}    1\n2\n

Log File
    Create File    ${TESTFILE}    hello world\nwith two lines
    ${file}=    Log File    ${TESTFILE}
    Should Be Equal    ${file}    hello world\nwith two lines

Log Latin-1 With Latin-1 Encoding
    ${file} =    Log File    ${LATIN-1 FILE}    Latin-1
    Should be equal    ${file}    ${RESULT}

Log File with 'ignore' Error Handler
    [Template]    Verify Log File with error handler
    ignore    Hyv t

Log File with 'replace' Error Handler
    [Template]    Verify Log File with error handler
    replace    Hyv\ufffd\ufffd \ufffd\ufffdt\ufffd

Get Binary File preserves CRLF line endings
    ${file}=    Get Binary File    ${UTF-8 WINDOWS FILE}
    ${expected}=    Encode String To Bytes    foo\r\nbar\r\n\foo bar\r\n\r\nÅÄÖ Föö\r\n    UTF-8
    Should Be Equal    ${file}    ${expected}

Get Binary File returns bytes as-is
    ${file}=    Get Binary File    ${LATIN-1 FILE}
    ${expected}=    Encode String To Bytes    Hyvää üötä    Latin-1
    Should Be Byte String    ${file}
    Should Be Equal    ${file}    ${expected}

Grep File
    [Template]    Grep And Check File
    ${EMPTY}    foo\nbar\nfoo bar\n\nA Foo
    foo         foo\nfoo bar
    foo?        foo bar
    ?foo        ${EMPTY}
    ?oo         foo\nfoo bar\nA Foo
    [Ff]oo      foo\nfoo bar\nA Foo
    f*a         foo bar
    ?           foo\nbar\nfoo bar\nA Foo
    ????        foo bar\nA Foo
    foo bar     foo bar

Grep File with regexp
    [Template]    Grep And Check File
    ${EMPTY}    foo\nbar\nfoo bar\n\nA Foo    regexp=True
    f\\wo       foo\nfoo bar                regexp=True
    foo.        foo bar                     regexp=True
    .foo        ${EMPTY}                    regexp=True
    .oo         foo\nfoo bar\nA Foo         regexp=True
    [Ff]oo      foo\nfoo bar\nA Foo         regexp=True
    f.*a        foo bar                     regexp=True
    .           foo\nbar\nfoo bar\nA Foo    regexp=True
    ....        foo bar\nA Foo              regexp=True
    foo\\sbar   foo bar                     regexp=True

Grep File with empty file
    Create File    ${TESTFILE}    ${EMPTY}
    Grep And Check File    *    ${EMPTY}    ${TESTFILE}

Grep File non Ascii
    [Setup]    Create File    ${TESTFILE}    fää\nbär\nföö bär\n\nA Fåå
    [Template]    Grep And Check File
    fää     fää        ${TESTFILE}
    ö       föö bär    ${TESTFILE}
    A       A Fåå      ${TESTFILE}

Grep File non Ascii with regexp
    [Setup]    Create File    ${TESTFILE}    fää\nbär\nföö bär\n\nA Fåå
    [Template]    Grep And Check File
    f\\wä    fää        ${TESTFILE}    regexp=True
    ö        föö bär    ${TESTFILE}    regexp=yes
    A        A Fåå      ${TESTFILE}    regexp=${True}

Grep File with UTF-16 files
    [Template]    Verify Grep File With UTF-16 files
    ${UTF-16 LE FILE}           UTF-16-LE    föö bar\nföö bar\nföö bar
    ${UTF-16 BE FILE}           UTF-16-BE    föö bar
    ${UTF-16 LE W/ BOM FILE}    UTF-16       föö bar\nföö bar\nföö bar\nföö bar
    ${UTF-16 BE W/ BOM FILE}    UTF-16       föö bar\nföö bar

Grep file with system encoding
    Create File    ${TEST FILE}    ${RESULT}\nSecond line\n${RESULT}    encoding=${SYSTEM_ENCODING}
    ${file} =    Grep file    ${TEST FILE}    ää ü    encoding=SYStem
    Should Be Equal    ${file}    ${RESULT}\n${RESULT}

Grep file with console encoding
    Create File    ${TEST FILE}    ${RESULT}\nSecond line\n${RESULT}\n     encoding=${CONSOLE_ENCODING}
    ${file} =    Grep file    ${TEST FILE}    ää ü    encoding=COnsoLE
    Should Be Equal    ${file}    ${RESULT}\n${RESULT}

Grep File with 'ignore' Error Handler
    [Template]    Verify Grep File with error handler
    ignore    f bar

Grep File with 'replace' Error Handler
    [Template]    Verify Grep File with error handler
    replace    f\ufffd\ufffd bar

Grep File With Windows line endings
    Grep And Check File    f*a    foo bar    ${UTF-8 WINDOWS FILE}
    Grep And Check File    f.*a    foo bar    ${UTF-8 WINDOWS FILE}    regexp=${True}

Path as `pathlib.Path`
    Create File    ${BASE}/file.txt    content\nthree\nlines
    ${content} =    Get File    ${PATH/'file.txt'}
    Should Be Equal    ${content}    content\nthree\nlines
    ${content} =    Grep File    ${PATH/'file.txt'}    t
    Should Be Equal    ${content}    content\nthree

*** Keywords ***
Get And Check File
    [Arguments]    ${path}    ${expected}
    ${content} =    Get File    ${path}
    Should Be Equal    ${content}    ${expected}

Grep And Check File
    [Arguments]    ${pattern}    ${expected}    ${test FILE}=${UTF-8 LONG FILE}    &{config}
    ${content} =    Grep File    ${test FILE}    ${pattern}    &{config}
    Should Be Equal    ${content}    ${expected}

Verify Get File with error handler
    [Arguments]    ${file}    ${error handler}    ${expected}
    ${ret}=    Get File    ${file}    ASCII    encoding_errors=${error handler}
    Should Be Equal    ${ret}    ${expected}

Verify Grep File with error handler
    [Arguments]    ${error handler}    ${expected}
    ${ret}=    Grep File    ${LATIN-1 LONG FILE}    f*a    ASCII    encoding_errors=${error handler}
    Should Be Equal    ${ret}    ${expected}

Verify Log File with error handler
    [Arguments]    ${error handler}    ${expected}
    ${ret}=    Log File    ${LATIN-1 FILE}    ASCII    encoding_errors=${error handler}
    Should Be Equal    ${ret}    ${expected}

Verify Grep File With UTF-16 files
    [Arguments]    ${file}    ${encoding}    ${expected}
    ${ret}=    Grep File    ${file}    f*a    ${encoding}
    Should Be Equal    ${ret}    ${expected}
