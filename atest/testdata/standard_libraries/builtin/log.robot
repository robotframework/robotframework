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

Log repr
    [Setup]    Set Log Level    DEBUG
    Log    Hyvää yötä \u2603!    repr=True
    Log    ${42}    DEBUG    ${FALSE}    ${FALSE}    ${TRUE}
    ${bytes} =    Evaluate    chr(0) + chr(255)
    Log    ${bytes}    repr=${42}
    ${list} =    Create List    Hyvä    \u2603    ${42}    ${bytes}
    Log    ${list}    repr=yes    console=please

Log pprint
    ${dict} =    Evaluate    {u'a long string': 1, u'a longer string!': 2, u'a much, much, much, much, much, much longer string': 3, u'list': [u'a long string', u'a longer string!', u'a much, much, much, much, much, much longer string']}
    Log    ${dict}    repr=true    console=please
    ${list} =    Evaluate    ['One', u'Two', 3]
    Log    ${list}    repr=yes    console=please
    ${list} =    Evaluate    ['a long string', u'a longer string!', u'a much, much, much, much, much, much longer string']
    Log    ${list}    repr=${1}    console=please
    ${dict} =    Evaluate    {u'a long string': 1, u'a longer string!': 2, u'a much, much, much, much, much, much longer string': 3, u'list': [u'a long string', u'a longer string!', u'a much, much, much, much, much, much longer string']}
    Log    ${dict}    repr=yes    console=no    html=NO
    ${list} =    Evaluate    [u'One', 'Two', 3]
    Log    ${list}    repr=yes
    ${dict} =    Evaluate    {u'a long string': 1, u'a longer string!': 2, u'a much, much, much, much, much, much longer string': 3, u'list': [u'a long string', ${42}, u'Hyvää yötä \u2603!', u'a much, much, much, much, much, much longer string', '\\x00\\xff']}
    Log    ${dict}    repr=yes    console=please

Log callable
    Log    ${MyObject}

Log Many
    Log Many    Log Many says:    1    2    ${3}    ${OBJ}
    Log Many    Log Many says: Hi!!
    Log Many    @{LIST}
    Log Many
    Log Many    @{EMPTY}
    Log Many    -${EMPTY}-    -@{EMPTY}-    -&{EMPTY}-
    Log Many    @{LIST}[0]    &{DICT}[b]

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
