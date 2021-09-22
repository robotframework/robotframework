*** Settings ***
Resource          libdoc_resource.robot

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

List some keywords
    Run Libdoc And Verify Output    ${TESTDATADIR}/resource.robot list o
    ...   Deprecation
    ...   Keyword with some "stuff" to <escape>
    ...   non ascii doc
    Run Libdoc And Verify Output    ${TESTDATADIR}/resource.robot LIST KW? C*R
    ...   curdir
    ...   kw 3
    ...   kw 4
    ...   kw 5
    ...   kw 6

Show whole library
    Run Libdoc And Set Output    ${TESTDATADIR}/module.py show
    Should Contain Intro    module
    ...    Version=0.1-alpha
    ...    Scope=GLOBAL
    Should Contain Keyword    Get Hello    ${EMPTY}
    ...    Get hello.
    ...    ${EMPTY}
    ...    See `importing` for explanation of nothing
    ...    and `introduction` for no more information
    Should Contain Keyword    Keyword    a1=d, *a2
    ...    A keyword.
    ...    ${EMPTY}
    ...    See `get hello` for details.

Show intro only
    Run Libdoc and set output    Telnet SHOW intro
    Should Contain Intro    Telnet    Version=
    ${args} =    Catenate    SEPARATOR=\n${SPACE*12}
    ...    timeout=3 seconds, newline=CRLF, prompt=None,
    ...    prompt_is_regexp=False, encoding=UTF-8, encoding_errors=ignore,
    ...    default_log_level=INFO, window_size=None, environ_user=None,
    ...    terminal_emulation=False, terminal_type=None,
    ...    telnetlib_log_level=TRACE, connection_timeout=None
    Should Contain Importing    ${args}
    ...    Telnet library can be imported with optional configuration parameters.
    Should Not Contain Keyword    Open Connection
    Should Not Contain Keyword    Write

Show intro and keywords
    Run Libdoc and set output    ${TESTDATADIR}/resource.robot SHOW NONASC* INTRO
    Should Contain Keyword    non ascii doc    ${EMPTY}
    ...    Hyvää yötä.
    ...    ${EMPTY}
    # Cannot test does output contain `Спасибо!` because consoles may not be able to show it.
    # Actually all consoles cannot show `Hyvää yötä` either but we expect western config.

Show version
    Run Libdoc And Verify Output    ${TESTDATADIR}/module.py version    0.1-alpha
    Run Libdoc And Verify Output    ${TESTDATADIR}/resource.robot version    N/A

*** Keywords ***
Should Contain Intro
    [Arguments]    ${name}    &{meta}
    ${underline} =    Evaluate    '=' * len($name)
    @{meta} =    Evaluate    [(n+':').ljust(10) + v for n, v in $meta.items()]
    ${expected} =    Catenate    SEPARATOR=\n
    ...    ${name}
    ...    ${underline}
    ...    @{meta}
    Should Contain    ${OUTPUT}    ${expected}

Should Contain Keyword
    [Arguments]    ${name}    ${args}    @{doc}
    ${underline} =    Evaluate    '-'*len('${name}')
    ${expected} =    Catenate    SEPARATOR=\n
    ...    ${name}
    ...    ${underline}
    ...    Arguments:${SPACE * 2}\[${args}]
    ...    ${EMPTY}
    ...    @{doc}
    Should Contain    ${OUTPUT}    ${expected}

Should Contain Importing
    [Arguments]    ${args}    @{doc}
    Should Contain Keyword    Importing    ${args}    @{doc}

Should Not Contain Keyword
    [Arguments]    ${name}
    ${underline} =    Evaluate    '-'*len('${name}')
    ${expected} =    Catenate    SEPARATOR=\n
    ...    ${name}
    ...    ${underline}
    Should Not Contain    ${OUTPUT}    ${expected}
