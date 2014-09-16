*** Settings ***
Test Teardown     Set Log Level    INFO
Variables         objects_for_call_method.py

*** Variables ***
${HTML}           <a href="http://robotframework.org">Robot Framework</a>

*** Test Cases ***
Log
    Log    Hello, world!
    Log    ${42}
    Log    ${None}
    Log    ${OBJ}

Log with different levels
    [Documentation]    FAIL Invalid log level 'INVALID'
    [Setup]    Set Log Level    TRACE
    Log    Log says: Hello from tests!
    Log    Trace level    TRACE
    Log    Debug level    debug
    Log    Info level    Info
    Log    Warn level    wArN
    Log    Fail level    FAIL
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

Log also to console
    [Setup]    Set Log Level    DEBUG
    Log    Hello, console!    console=yepyep
    Log    ${HTML}    debug    enable both html    and console

Log repr
    [Setup]    Set Log Level    DEBUG
    Log    Hyvää yötä \u2603!    repr=True
    Log    ${42}    DEBUG    ${FALSE}    ${FALSE}    ${TRUE}
    ${bytes} =    Evaluate    chr(0) + chr(255)
    Log    ${bytes}    repr=yes
    ${list} =    Create List    Hyvä    \u2603    ${42}    ${bytes}
    Log    ${list}    repr=yes    console=please

Log pprint
    ${dict} =    Evaluate    {'a long string': 1, 'a longer string!': 2, 'a much, much, much, much, much, much longer string': 3, 'list': ['a long string', 'a longer string!', 'a much, much, much, much, much, much longer string']}
    Log    ${dict}    repr=yes    console=please
    ${list} =    Evaluate    ['One', 'Two', 3]
    Log    ${list}    repr=yes    console=please
    ${list} =    Evaluate    ['a long string', 'a longer string!', 'a much, much, much, much, much, much longer string']
    Log    ${list}    repr=yes    console=please
    ${dict} =    Evaluate    {'a long string': 1, 'a longer string!': 2, 'a much, much, much, much, much, much longer string': 3, 'list': ['a long string', 'a longer string!', 'a much, much, much, much, much, much longer string']}
    Log    ${dict}    repr=yes
    ${list} =    Evaluate    ['One', 'Two', 3]
    Log    ${list}    repr=yes
    ${dict} =    Evaluate    {'a long string': 1, 'a longer string!': 2, 'a much, much, much, much, much, much longer string': 3, 'list': ['a long string', ${42}, u'Hyvää yötä \u2603!', 'a much, much, much, much, much, much longer string', '\\x00\\xff']}
    Log    ${dict}    repr=yes    console=please

Log callable
    Log    ${MyObject}

Log Many
    Log Many    Log Many says:    Hello    from    tests!
    Log Many    Log Many says: Hi!!

Log to console
    Log To Console    stdout äö w/ newline
    Log To Console    stdout äö w/o new...    no_newline=true
    Log To Console    stderr äö w/ newline    stdERR
    Log To Console    ...line äö   stdout    continue without newlines
    Log To Console    ${42}
