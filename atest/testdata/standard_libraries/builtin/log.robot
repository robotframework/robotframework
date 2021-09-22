*** Settings ***
Test Teardown     Set Log Level    INFO
Variables         objects_for_call_method.py

*** Variables ***
${HTML}           <a href="http://robotframework.org">Robot Framework</a>
@{LIST}           1    2    ${3}    ${OBJ}
&{DICT}           a=1    b=2    ${3}=c    obj=${OBJ}

*** Test Cases ***
Log
    Log    Hello, world!
    Log    ${42}
    Log    ${None}
    Log    ${OBJ}

Log with different levels
    [Documentation]    FAIL Invalid log level 'INVALID'.
    [Setup]    Set Log Level    TRACE
    Log    Log says: Hello from tests!
    Log    Trace level    TRACE
    Log    Debug level    debug
    Log    Info level    Info
    Log    Warn level    wArN
    Log    Error level    ERROR
    Log    Invalid level    INVALID

HTML is escaped by default
    Log    <b>not bold</b>
    Log    ${HTML}

HTML pseudo level
    Log    <b>bold</b>    HTML
    Log    ${HTML}    HTML

Explicit HTML
    [Setup]    Set Log Level    DEBUG
    Log    <b>bold</b>    html=yep
    Log    ${HTML}    DEBUG    xxx
    Log    ${HTML}    html=${FALSE}    level=debug

FAIL is not valid log level
    [Documentation]    FAIL Invalid log level 'FAIL'.
    Log    This fails    FAIL

Log also to console
    [Setup]    Set Log Level    DEBUG
    Log    Hello, console!    console=yepyep    repr=no    html=false
    Log    ${HTML}    debug    enable both html    and console

repr=True
    [Setup]    Set Log Level    DEBUG
    Log    Nothing special here    repr=yes
    Log    Hyvää yötä \u2603!    repr=True
    Log    ${42}    DEBUG    ${FALSE}    ${FALSE}    ${TRUE}
    ${bytes} =    Evaluate    b'\\x00abc\\xff (repr=True)'
    Log    ${bytes}    repr=${42}    console=True
    ${nfd} =    Evaluate    'hyva\u0308'
    Log    ${nfd}    repr=Y

formatter=repr
    [Setup]    Set Log Level    DEBUG
    Log    Nothing special here    formatter=repr
    Log    Hyvää yötä \u2603!    formatter=repr
    Log    ${42}    DEBUG    ${FALSE}    ${FALSE}    ${TRUE}
    ${bytes} =    Evaluate    b'\\x00abc\\xff (formatter=repr)'
    Log    ${bytes}    formatter=REPR    console=True
    ${nfd} =    Evaluate    'hyva\u0308'
    Log    ${nfd}    formatter=Repr

formatter=ascii
    [Setup]    Set Log Level    DEBUG
    Log    Nothing special here    formatter=ascii
    Log    Hyvää yötä \u2603!    formatter=ascii
    Log    ${42}    DEBUG    ${FALSE}    ${FALSE}    ${TRUE}
    ${bytes} =    Evaluate    b'\\x00abc\\xff (formatter=ascii)'
    Log    ${bytes}    formatter=ASCII    console=True
    ${nfd} =    Evaluate    'hyva\u0308'
    Log    ${nfd}    formatter=Ascii

formatter=str
    [Setup]    Set Log Level    DEBUG
    Log    Nothing special here    formatter=str
    Log    Hyvää yötä \u2603!    formatter=STR
    Log    ${42}    DEBUG    ${FALSE}    ${FALSE}    ${TRUE}
    ${bytes} =    Evaluate    b'\\x00abc\\xff (formatter=str)'
    Log    ${bytes}    formatter=str    console=True
    ${nfd} =    Evaluate    'hyva\u0308'
    Log    ${nfd}    formatter=str

formatter=repr pretty prints
    ${long string} =    Evaluate    ' '.join(['Robot Framework'] * 1000)
    Log    ${long string}    repr=True
    ${small dict} =    Evaluate    {'small': 'dict', 3: b'items', 'a': 'sorted'}
    Log    ${small dict}    formatter=repr    console=TRUE
    ${big dict} =    Evaluate    {'big': 'dict', 'long': '${long string}', 'nested': ${small dict}, 'list': [1, 2, 3]}
    Log    ${big dict}    html=NO    formatter=repr
    ${small list} =    Evaluate    ['small', b'list', 'not sorted', 4]
    Log    ${small list}    console=gyl    formatter=repr
    ${big list} =    Evaluate    ['big', 'list', '${long string}', b'${long string}', ['nested', ('tuple', 2)], ${small dict}]
    Log    ${big list}    formatter=repr
    ${non ascii} =    Evaluate    ['hyv\\xe4', b'hyv\\xe4', {'\\u2603': b'\\x00\\xff'}]
    Log    ${non ascii}    formatter=repr

formatter=invalid
    [Documentation]    FAIL ValueError: Invalid formatter 'invalid'. Available 'str', 'repr' and 'ascii'.
    Log    x    formatter=invalid

Log callable
    Log    ${MyObject}
    ${lambda} =    Evaluate    lambda: None
    Log    ${lambda}

Log Many
    Log Many    Log Many says:    1    2    ${3}    ${OBJ}
    Log Many    Log Many says: Hi!!
    Log Many    @{LIST}
    Log Many
    Log Many    @{EMPTY}
    Log Many    -${EMPTY}-    -@{EMPTY}-    -&{EMPTY}-
    Log Many    ${LIST}[0]    ${DICT}[b]

Log Many with named and dict arguments
    Log Many    a=1    b=2    ${3}=c    obj=${OBJ}
    Log Many    &{DICT}
    Log Many    &{DICT}    b=no override    &{EMPTY}    ${3}=three

Log Many with positional, named and dict arguments
    Log Many    1    ${2}    three=3    &{EMPTY}    ${4}=four
    Log Many    @{LIST}    &{DICT}    @{LIST}    &{DICT}

Log Many with non-existing variable
    [Documentation]    FAIL Variable '${no such variable}' not found.
    Log Many    ${no such variable}

Log Many with list variable containing non-list
    [Documentation]    FAIL Value of variable '@{HTML}' is not list or list-like.
    Log Many    @{HTML}

Log Many with dict variable containing non-dict
    [Documentation]    FAIL Value of variable '&{LIST}' is not dictionary or dictionary-like.
    Log Many    &{LIST}

Log To Console
    Log To Console    stdout äö w/ newline
    Log To Console    stdout äö w/o new...    no_newline=true
    Log To Console    stderr äö w/ newline    stdERR
    Log To Console    ...line äö   stdout    continue without newlines
    Log To Console    ${42}
