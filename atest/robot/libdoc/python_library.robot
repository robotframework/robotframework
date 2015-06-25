*** Settings ***
Suite Setup       Run Libdoc And Parse Output    Telnet
Force Tags        regression    pybot    jybot
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be    Telnet

Documentation
    Doc Should Start With
    ...    A test library providing communication over Telnet connections.\n\n
    ...    ``Telnet`` is Robot Framework's standard library that makes it possible to\n

Version
    Version Should Match    *

Type
    Type Should Be    library

Generated
    Generated Should Be Defined

Scope
    Scope Should Be    test suite

Named Args
    Named Args Should Be    yes

Init Documentation
    Init Doc Should Start With    0
    ...    Telnet library can be imported with optional configuration parameters.\n\n
    ...    Configuration parameters are used as default values when new\nconnections are

Init Arguments
    Init Arguments Should Be    0    timeout=3 seconds    newline=CRLF
    ...    prompt=None    prompt_is_regexp=False    encoding=UTF-8
    ...    encoding_errors=ignore    default_log_level=INFO     window_size=None
    ...    environ_user=None    terminal_emulation=False    terminal_type=None
    ...    telnetlib_log_level=TRACE

Keyword Names
    Keyword Name Should Be     0    Close All Connections
    Keyword Name Should Be     1    Close Connection

Keyword Arguments
    Keyword Arguments Should Be     0
    Keyword Arguments Should Be     1     loglevel=None

Keyword Documentation
    Keyword Doc Should Start With    0   Closes all open connections
    Keyword Doc Should Start With    2
    ...    Executes the given ``command`` and reads, logs, and returns everything until the prompt.\n\n
    ...    This keyword requires the prompt to be [#Configuration|configured]\n
    ...    either in `importing` or with `Open Connection` or `Set Prompt` keyword.\n\n
    ...    This is a convenience keyword that uses `Write` and `Read Until Prompt`\n
    ...    internally. Following two examples are thus functionally identical:\n\n
    ...    | \${out} = | `Execute Command`${SPACE*3}| pwd |\n\n
    ...    | `Write`${SPACE*2}| pwd${SPACE*17}|\n
    ...    | \${out} = | `Read Until Prompt` |\n\n

KwArgs and VarArgs
    Run Libdoc And Parse Output    Process
    Keyword Name Should Be         6    Run Process
    Keyword Arguments Should Be    6    command    *arguments    **configuration

Documentation set in __init__
    Run Libdoc And Parse Output    ${TESTDATADIR}/DocSetInInit.py
    Doc Should Be    Doc set in __init__!!
