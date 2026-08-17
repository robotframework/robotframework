*** Settings ***
Resource          libdoc_resource.robot

*** Variables ***
${DEPRECATION}    [[] WARN ] Invalid documentation in 'kw 6': Not having an empty row before 'Tags:' is deprecated.

*** Test Cases ***
List all keywords
    Run Libdoc And Verify Output    ${TESTDATADIR}/module.py list
    ...   Get Hello
    ...   Keyword
    ...   Keyword With Tags 1
    ...   Keyword with tags 2
    ...   Keyword With Tags 3
    ...   Multiline Doc With Split Short Doc
    ...   Non Ascii Bytes Defaults
    ...   Non Ascii Doc
    ...   Non Ascii Doc With Escapes
    ...   Non Ascii String Defaults
    ...   Non String Defaults
    ...   Robot Espacers
    ...   Set Name Using Robot Name Attribute
    ...   Takes \${embedded} \${args}
    ...   Takes \${embedded} and normal args
    ...   Takes \${embedded} and positional-only args

List some keywords
    Run Libdoc And Verify Output    ${TESTDATADIR}/resource.robot list o
    ...   ${DEPRECATION}
    ...   Deprecation
    ...   Keyword with some "stuff" to <escape>
    ...   non ascii doc
    ...   With embedded \${arg: int} and normal arg
    Run Libdoc And Verify Output    ${TESTDATADIR}/resource.robot LIST KW? C*R
    ...   ${DEPRECATION}
    ...   curdir
    ...   kw 3
    ...   kw 4
    ...   kw 5
    ...   kw 6

Show whole library
    Run Libdoc And Set Output    ${TESTDATADIR}/module.py show
    Should Contain    ${OUTPUT}    \## Keywords
    Should Contain Intro    \# module
    ...    Version=0.1-alpha
    ...    Scope=GLOBAL
    Should Contain Keyword    Get Hello    ${EMPTY}    ${EMPTY}
    ...    Get hello.
    ...    ${EMPTY}
    ...    See `importing` for explanation of nothing
    ...    and `introduction` for no more information
    VAR    @{args}    `a1` (default: `d`)    `*a2`
    Should Contain Keyword    Keyword    ${args}    ${EMPTY}
    ...    A keyword.
    ...    ${EMPTY}
    ...    See `get hello` for details.

Show intro only
    Run Libdoc and set output    Telnet SHOW intro
    Should Contain Intro    Telnet    Version=
    VAR    @{args}
    ...    `timeout` (default: `3 seconds`)
    ...    `newline` (default: `CRLF`)
    ...    `prompt` (default: `None`)
    ...    `prompt_is_regexp` (default: `False`)
    ...    `encoding` (default: `UTF-8`)
    ...    `encoding_errors` (default: `ignore`)
    ...    `default_log_level` (default: `INFO`)
    ...    `window_size` (default: `None`)
    ...    `environ_user` (default: `None`)
    ...    `terminal_emulation` (default: `False`)
    ...    `terminal_type` (default: `None`)
    ...    `telnetlib_log_level` (default: `TRACE`)
    ...    `connection_timeout` (default: `None`)
    Should Contain Importing    ${args}
    ...    Telnet library can be imported with optional configuration parameters.
    Should Not Contain Keyword    Open Connection
    Should Not Contain Keyword    Write

Show intro and keywords
    Run Libdoc and set output    ${TESTDATADIR}/resource.robot SHOW NONASC* INTRO
    VAR    @{tags}    `common`
    Should Contain Keyword    non ascii doc    ${EMPTY}
    ...    ${tags}
    ...    Hyvää yötä.
    ...    ${EMPTY}
    # Cannot test does output contain `Спасибо!` because consoles may not be able to show it.
    # Actually all consoles cannot show `Hyvää yötä` either but we expect western config.

Show markdown libary
    Run Libdoc and set output    ${TESTDATADIR}/MarkdownLibrary.py show
    Compare Against Golden Image    ${TESTDATADIR}/MarkdownLibrary.txt

Show version
    Run Libdoc And Verify Output    ${TESTDATADIR}/module.py version
    ...    0.1-alpha
    Run Libdoc And Verify Output    ${TESTDATADIR}/resource.robot version
    ...    ${DEPRECATION}
    ...    N/A

*** Keywords ***
Should Contain Intro
    [Arguments]    ${name}    &{meta}
    @{meta} =    Evaluate    [f"* {n}: {v}" for n, v in $meta.items()]
    ${expected} =    Catenate    SEPARATOR=\n
    ...    ${name}
    ...    ${EMPTY}
    ...    @{meta}
    Should Contain    ${OUTPUT}    ${expected}

Compare Against Golden Image
    [Arguments]    ${file}
    ${expected} =    Get File    ${file}
    Should Be Equal    ${OUTPUT}    ${expected}

Should Contain Keyword
    [Arguments]    ${name}    ${args}    ${tags}    @{doc}
    IF    $name == 'Importing'
        VAR    ${heading}    \##
    ELSE
        VAR    ${heading}    \###
    END
    ${expected} =    Catenate    SEPARATOR=\n
    ...    ${heading} ${name}
    IF    $args
        ${args}    Evaluate    [f"* {a}" for a in $args]
        ${expected}    Catenate    SEPARATOR=\n
        ...    ${expected}
        ...    ${EMPTY}
        ...    **Arguments:**
        ...    ${EMPTY}
        ...    @{args}
    END
    IF    $tags
        ${tags}    Evaluate    [f"* {t}" for t in $tags]
        ${expected}    Catenate    SEPARATOR=\n
        ...    ${expected}
        ...    ${EMPTY}
        ...    **Tags:**
        ...    ${EMPTY}
        ...    @{tags}
    END

    ${expected}    Catenate    SEPARATOR=\n
    ...    ${expected}
    ...    ${EMPTY}
    ...    @{doc}
    Should Contain    ${OUTPUT}    ${expected}

Should Contain Importing
    [Arguments]    ${args}    @{doc}
    Should Contain Keyword    Importing    ${args}    ${EMPTY}    @{doc}

Should Not Contain Keyword
    [Arguments]    ${name}
    ${underline} =    Evaluate    '-'*len('${name}')
    ${expected} =    Catenate    SEPARATOR=\n
    ...    ${name}
    ...    ${underline}
    Should Not Contain    ${OUTPUT}    ${expected}
