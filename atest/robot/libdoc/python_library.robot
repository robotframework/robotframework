*** Settings ***
Suite Setup       Run Libdoc And Parse Output    Telnet
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be                   Telnet

Documentation
    Doc Should Start With
    ...    A test library providing communication over Telnet connections.
    ...
    ...    ``Telnet`` is Robot Framework's standard library that makes it possible to

Version
    Version Should Match             3.*

Type
    Type Should Be                   library

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                  test suite

Named Args
    Named Args Should Be             yes

Init Documentation
    Init Doc Should Start With       0
    ...    Telnet library can be imported with optional configuration parameters.\n\n
    ...    Configuration parameters are used as default values when new\nconnections are

Init Arguments
    Init Arguments Should Be         0    timeout=3 seconds    newline=CRLF
    ...    prompt=None    prompt_is_regexp=False    encoding=UTF-8
    ...    encoding_errors=ignore    default_log_level=INFO     window_size=None
    ...    environ_user=None    terminal_emulation=False    terminal_type=None
    ...    telnetlib_log_level=TRACE    connection_timeout=None

Keyword Names
    Keyword Name Should Be           0    Close All Connections
    Keyword Name Should Be           1    Close Connection

Keyword Arguments
    Keyword Arguments Should Be      0
    Keyword Arguments Should Be      1     loglevel=None

Keyword Documentation
    Keyword Doc Should Start With    0   Closes all open connections
    Keyword Doc Should Start With    2
    ...    Executes the given ``command`` and reads, logs, and returns everything until the prompt.
    ...
    ...    This keyword requires the prompt to be [#Configuration|configured]
    ...    either in `importing` or with `Open Connection` or `Set Prompt` keyword.
    ...
    ...    This is a convenience keyword that uses `Write` and `Read Until Prompt`
    ...    internally. Following two examples are thus functionally identical:\
    ...
    ...    | \${out} = | `Execute Command`${SPACE*3}| pwd |
    ...
    ...    | `Write`${SPACE*2}| pwd${SPACE*17}|
    ...    | \${out} = | `Read Until Prompt` |
    ...

KwArgs and VarArgs
    Run Libdoc And Parse Output      Process
    Keyword Name Should Be           7    Run Process
    Keyword Arguments Should Be      7    command    *arguments    **configuration

Keyword-only Arguments
    [Tags]    require-py3
    Run Libdoc And Parse Output      ${TESTDATADIR}/KeywordOnlyArgs.py
    Keyword Arguments Should Be      0    *    kwo
    Keyword Arguments Should Be      1    *varargs    kwo    another=default

Decorators
    Run Libdoc And Parse Output      ${TESTDATADIR}/Decorators.py
    Keyword Name Should Be           0    Keyword Using Decorator
    Keyword Arguments Should Be      0    *args    **kwargs
    Keyword Name Should Be           1    Keyword Using Decorator With Wraps
    Run Keyword If    $INTERPRETER.is_py3
    ...    Keyword Arguments Should Be      1    args    are    preserved=True
    ...    ELSE
    ...    Keyword Arguments Should Be      1    *args    **kwargs

Documentation set in __init__
    Run Libdoc And Parse Output      ${TESTDATADIR}/DocSetInInit.py
    Doc Should Be                    Doc set in __init__!!

Deprecation
    Run Libdoc And Parse Output          ${TESTDATADIR}/Deprecation.py
    Keyword Name Should Be               0    Deprecated
    Keyword Doc Should Be                0    *DEPRECATED*
    Keyword Should Be Deprecated         0
    Keyword Name Should Be               1    Deprecated With Message
    Keyword Doc Should Be                1    *DEPRECATED for some good reason!* Yes it is. For sure.
    Keyword Should Be Deprecated         1
    Keyword Name Should Be               2    No Deprecation Whatsoever
    Keyword Doc Should Be                2
    Keyword Should Not Be Deprecated     2
    Keyword Name Should Be               3    Silent Deprecation
    Keyword Doc Should Be                3    *Deprecated* but not yet loudly.
    ...
    ...                                       RF and Libdoc don't consider this being deprecated.
    Keyword Should Not Be Deprecated     3
