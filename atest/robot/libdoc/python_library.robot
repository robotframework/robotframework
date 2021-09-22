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
    Version Should Match             [345].*

Type
    Type Should Be                   LIBRARY

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                  SUITE

Source info
    Source should be                 ${CURDIR}/../../../src/robot/libraries/Telnet.py
    Lineno should be                 36

Spec version
    Spec version should be correct

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

Init Source Info
    Keyword Should Not Have Source   0    xpath=inits/init
    Keyword Lineno Should Be         0    281      xpath=inits/init

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

Keyword Source Info
    # This keyword is from the "main library".
    Keyword Name Should Be           0    Close All Connections
    Keyword Should Not Have Source   0
    Keyword Lineno Should Be         0    470
    # This keyword is from an external library component.
    Keyword Name Should Be           7    Read Until Prompt
    Keyword Should Not Have Source   7
    Keyword Lineno Should Be         7    1011

KwArgs and VarArgs
    Run Libdoc And Parse Output      Process
    Keyword Name Should Be           7    Run Process
    Keyword Arguments Should Be      7    command    *arguments    **configuration

Keyword-only Arguments
    Run Libdoc And Parse Output      ${TESTDATADIR}/KeywordOnlyArgs.py
    Keyword Arguments Should Be      0    *    kwo
    Keyword Arguments Should Be      1    *varargs    kwo    another=default

Positional-only Arguments
    [Tags]    require-py3.8
    Run Libdoc And Parse Output      ${DATADIR}/keywords/PositionalOnly.py
    Keyword Arguments Should Be      2    arg    /
    Keyword Arguments Should Be      5    posonly    /    normal
    Keyword Arguments Should Be      0    required    optional=default    /
    Keyword Arguments Should Be      4    first: int    second: float    /

Decorators
    Run Libdoc And Parse Output      ${TESTDATADIR}/Decorators.py
    Keyword Name Should Be           0    Keyword Using Decorator
    Keyword Arguments Should Be      0    *args    **kwargs
    Keyword Should Not Have Source   0
    Keyword Lineno Should Be         0    8
    Keyword Name Should Be           1    Keyword Using Decorator With Wraps
    Keyword Arguments Should Be      1    args    are    preserved=True
    Keyword Lineno Should Be         1    26

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
