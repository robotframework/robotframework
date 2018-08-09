*** Settings ***
Library           PythonAnnotations.py

*** Variables ***
@{LIST}           foo         bar
&{DICT}           foo=${1}    bar=${2}

*** Test Cases ***
Integer
    Integer       42                      ${42}
    Integer       -1                      ${-1}

Float as integer
    Integer       1.0                     ${1.0}
    Integer       1.5                     ${1.5}

Invalid integer
    [Template]    Conversion Should Fail
    Integer       foobar

Float
    Float         1.5                     ${1.5}
    Float         -1                      ${-1.0}

Invalid float
    [Template]    Conversion Should Fail
    Float         foobar

Decimal
    Decimal       3.14                    Decimal('3.14')
    Decimal       -1                      Decimal('-1')
    Decimal       1e6                     Decimal('1000000')

Invalid decimal
    [Template]    Conversion Should Fail
    Decimal       foobar

Boolean
    Boolean       True                    ${True}
    Boolean       false                   ${False}
    Boolean       no                      ${False}
    Boolean       none                    ${None}

Invalid boolean is accepted as-is
    Boolean       FooBar                  "FooBar"
    Boolean       ${EMPTY}                ""

List
    List          []                      []
    List          ['foo', 'bar']          ${LIST}
    List          [1, 2, 3.14, -42]       [1, 2, 3.14, -42]
    List          ['\\x00', '\\x52']      ['\\x00', 'R']

Invalid list
    [Template]    Conversion Should Fail
    List          [1, ooops]
    List          {}
    List          ooops
    List          ${EMPTY}
    List          !"#¤%&/()=?

Tuple
    Tuple         ()                      ()
    Tuple         ('foo', "bar")          tuple(${LIST})
    Tuple         (1, 2, 3.14, -42)       (1, 2, 3.14, -42)

Invalid tuple
    [Template]    Conversion Should Fail
    Tuple         (1, ooops)
    Tuple         {}
    Tuple         ooops

Dictionary
    Dictionary    {}                      {}
    Dictionary    {'foo': 1, "bar": 2}    dict(${DICT})
    Dictionary    {1: 2, 3.14: -42}       {1: 2, 3.14: -42}

Invalid dictionary
    [Template]    Conversion Should Fail
    Dictionary    {1: ooops}
    Dictionary    []
    Dictionary    ooops
    Dictionary    {{'not': 'hashable'}: 'value'}

Set
    Set           set()                   set()
    Set           {'foo', 'bar'}          {'foo', 'bar'}
    Set           {1, 2, 3.14, -42}       {1, 2, 3.14, -42}

Invalid set
    [Template]    Conversion Should Fail
    Set           {1, ooops}
    Set           {}
    Set           ooops
    Set           {{'not', 'hashable'}}

Iterable abc
    Iterable      ['list', 'is', 'ok']    ['list', 'is', 'ok']
    Iterable      ('tuple',)              ('tuple',)
    Iterable      set()                   set()
    Iterable      {'dict': 'accepted'}    {'dict': 'accepted'}

Invalid iterable abc
    [Template]    Conversion Should Fail
    Iterable      foobar

Mapping abc
    Mapping            {'foo': 1, 2: 'bar'}    {'foo': 1, 2: 'bar'}
    Mutable mapping    {'foo': 1, 2: 'bar'}    {'foo': 1, 2: 'bar'}

Invalid mapping abc
    [Template]    Conversion Should Fail
    Mapping            foobar
    Mutable mapping    barfoo                  type=mapping

Set abc
    Set abc       set()                   set()
    Set abc       {'foo', 'bar'}          {'foo', 'bar'}
    Set abc       {1, 2, 3.14, -42}       {1, 2, 3.14, -42}
    Mutable set   set()                   set()
    Mutable set   {'foo', 'bar'}          {'foo', 'bar'}
    Mutable set   {1, 2, 3.14, -42}       {1, 2, 3.14, -42}

Invalid set abc
    [Template]    Conversion Should Fail
    Set abc       {1, ooops}              type=set
    Set abc       {}                      type=set
    Set abc       ooops                   type=set
    Mutable set   {1, ooops}              type=set
    Mutable set   {}                      type=set
    Mutable set   ooops                   type=set

Enum
    Enum          BAR                     Foo.BAR

Invalid Enum
    [Template]    Conversion Should Fail
    Enum          foobar                  type=Foo

Bytes
    Bytes         foo                     b'foo'
    Bytes         \x00\x01\xFF\u00FF      b'\\x00\\x01\\xFF\\xFF'
    Bytes         Hyvä esimerkki!         b'Hyv\\xE4 esimerkki!'

Invalid bytes
    [Template]    Conversion Should Fail
    Bytes         \u0100

Datetime
    DateTime      2014-06-11T10:07:42     datetime(2014, 6, 11, 10, 7, 42)
    DateTime      20180808144342123456    datetime(2018, 8, 8, 14, 43, 42, 123456)
    DateTime      1975:06:04              datetime(1975, 6, 4)

Invalid datetime
    [Template]    Conversion Should Fail
    DateTime      foobar
    DateTime      1975:06
    DateTime      2018
    DateTime      201808081443421234567

Date
    Date          2014-06-11              date(2014, 6, 11)
    Date          20180808                date(2018, 8, 8)
    Date          20180808000000000000    date(2018, 8, 8)

Invalid date
    [Template]    Conversion Should Fail
    Date          foobar
    Date          1975:06
    Date          2018
    Date          2014-06-11T10:07:42
    Date          20180808000000000001

Timedelta
    Timedelta     10                      timedelta(seconds=10)
    Timedelta     -1.5                    timedelta(seconds=-1.5)
    Timedelta     2 days 1 second         timedelta(2, 1)
    Timedelta     5d 4h 3min 2s 1ms       timedelta(5, 4*60*60 + 3*60 + 2 + 0.001)
    Timedelta     - 1 day 2 seconds       timedelta(-1, -2)
    Timedelta     1.5 minutes             timedelta(seconds=90)
    Timedelta     04:03:02.001            timedelta(seconds=4*60*60 + 3*60 + 2 + 0.001)
    Timedelta     4:3:2.1                 timedelta(seconds=4*60*60 + 3*60 + 2 + 0.1)
    Timedelta     100:00:00               timedelta(seconds=100*60*60)
    Timedelta     -00:01                  timedelta(seconds=-1)

Invalid timedelta
    [Template]    Conversion Should Fail
    Timedelta     foobar
    Timedelta     1 foo
    Timedelta     01:02:03:04

String is not converted
    String        Hello, world!           "Hello, world!"
    String        åäö                     "åäö"

Unknown types are not converted
    Unknown       foo                     "foo"
    Unknown       1                       "1"
    Unknown       true                    "true"
    Unknown       None                    "None"
    Unknown       none                    "none"

Non-strings are not converted
    [Template]    Non-string is not converted
    Integer
    Float
    Boolean
    Decimal
    List
    Tuple
    Dictionary
    Set
    Enum
    Bytes
    DateTime
    Date
    Timedelta

String None is converted to None object
    [Template]    String None is converted to None object
    Integer
    Float
    Boolean
    Decimal
    List
    Tuple
    Dictionary
    Set
    Enum
    Bytes
    DateTime
    Date
    Timedelta

*** Keywords ***
Conversion Should Fail
    [Arguments]    ${kw}    ${arg}    ${type}=${kw.lower()}
    ${error} =    Run Keyword And Expect Error    *    ${kw}    ${arg}
    Should Be Equal    ${error}
    ...    ValueError: Argument 'argument' cannot be converted to ${type}, got '${arg}'.

Non-string is not converted
    [Arguments]    ${kw}
    Run Keyword    ${kw}    ${1}       ${1}
    Run Keyword    ${kw}    ${1.5}     ${1.5}
    Run Keyword    ${kw}    ${True}    ${True}
    Run Keyword    ${kw}    ${None}    ${None}
    Run Keyword    ${kw}    ${LIST}    ${LIST}
    Run Keyword    ${kw}    ${DICT}    ${DICT}

String None is converted to None object
    [Arguments]    ${kw}
    Run Keyword    ${kw}    None       ${None}
    Run Keyword    ${kw}    NONE       ${None}
    Run Keyword    ${kw}    none       ${None}
