*** Settings ***
Library                  AnnotationsWithAliases.py
Resource                 conversion.resource

*** Variables ***
@{LIST}                  foo                       bar
&{DICT}                  foo=${1}                  bar=${2}

*** Test Cases ***
Integer
    Integer              42                        ${42}
    Int                  -1                        ${-1}
    Long                 9999999999999999999999    ${9999999999999999999999}

Invalid integer
    [Template]           Conversion Should Fail
    Integer              foobar
    Int                  1.0                       type=integer

Float
    Float                1.5                       ${1.5}
    Double               -1                        ${-1.0}
    Float                1e6                       ${1000000.0}
    Double               -1.2e-3                   ${-0.0012}

Invalid float
    [Template]           Conversion Should Fail
    Float                foobar

Decimal
    Decimal              3.14                      Decimal('3.14')
    Decimal              -1                        Decimal('-1')
    Decimal              1e6                       Decimal('1000000')

Invalid decimal
    [Template]           Conversion Should Fail
    Decimal              foobar

Boolean
    Boolean              True                      ${True}
    Bool                 YES                       ${True}
    Boolean              on                        ${True}
    Bool                 1                         ${True}
    Boolean              false                     ${False}
    Bool                 No                        ${False}
    Boolean              oFF                       ${False}
    Bool                 0                         ${False}
    Boolean              ${EMPTY}                  ${False}
    Bool                 none                      ${None}

Invalid boolean is accepted as-is
    Boolean              FooBar                    'FooBar'
    Bool                 42                        '42'

String
    String               Hello, world!             'Hello, world!'
    String               åäö                       'åäö'
    String               None                      'None'
    String               True                      'True'
    String               []                        '[]'

Bytes
    Bytes                foo                       b'foo'
    Bytes                \x00\x01\xFF\u00FF        b'\\x00\\x01\\xFF\\xFF'
    Bytes                Hyvä esimerkki!           b'Hyv\\xE4 esimerkki!'
    Bytes                None                      b'None'
    Bytes                NONE                      b'NONE'

Invalid bytes
    [Template]           Conversion Should Fail
    Bytes                \u0100                                          error=Character '\u0100' cannot be mapped to a byte.
    Bytes                \u00ff\u0100\u0101                              error=Character '\u0100' cannot be mapped to a byte.
    Bytes                Hyvä esimerkki! \u2603                          error=Character '\u2603' cannot be mapped to a byte.

Bytearray
    Bytearray            foo                       bytearray(b'foo')
    Bytearray            \x00\x01\xFF\u00FF        bytearray(b'\\x00\\x01\\xFF\\xFF')
    Bytearray            Hyvä esimerkki!           bytearray(b'Hyv\\xE4 esimerkki!')
    Bytearray            None                      bytearray(b'None')
    Bytearray            NONE                      bytearray(b'NONE')

Invalid bytearray
    [Template]           Conversion Should Fail
    Bytearray            \u0100                                          error=Character '\u0100' cannot be mapped to a byte.
    Bytearray            \u00ff\u0100\u0101                              error=Character '\u0100' cannot be mapped to a byte.
    Bytearray            Hyvä esimerkki! \u2603                          error=Character '\u2603' cannot be mapped to a byte.

Datetime
    DateTime             2014-06-11T10:07:42       datetime(2014, 6, 11, 10, 7, 42)
    DateTime             20180808144342123456      datetime(2018, 8, 8, 14, 43, 42, 123456)
    DateTime             1975:06:04                datetime(1975, 6, 4)

Invalid datetime
    [Template]           Conversion Should Fail
    DateTime             foobar                                          error=Invalid timestamp 'foobar'.
    DateTime             1975:06                                         error=Invalid timestamp '1975:06'.
    DateTime             2018                                            error=Invalid timestamp '2018'.
    DateTime             201808081443421234567                           error=Invalid timestamp '201808081443421234567'.

Date
    Date                 2014-06-11                date(2014, 6, 11)
    Date                 20180808                  date(2018, 8, 8)
    Date                 20180808000000000000      date(2018, 8, 8)

Invalid date
    [Template]           Conversion Should Fail
    Date                 foobar                                          error=Invalid timestamp 'foobar'.
    Date                 1975:06                                         error=Invalid timestamp '1975:06'.
    Date                 2018                                            error=Invalid timestamp '2018'.
    Date                 2014-06-11T10:07:42                             error=Value is datetime, not date.
    Date                 20180808000000000001                            error=Value is datetime, not date.

Timedelta
    Timedelta            10                        timedelta(seconds=10)
    Timedelta            -1.5                      timedelta(seconds=-1.5)
    Timedelta            2 days 1 second           timedelta(2, 1)
    Timedelta            5d 4h 3min 2s 1ms         timedelta(5, 4*60*60 + 3*60 + 2 + 0.001)
    Timedelta            - 1 day 2 seconds         timedelta(-1, -2)
    Timedelta            1.5 minutes               timedelta(seconds=90)
    Timedelta            04:03:02.001              timedelta(seconds=4*60*60 + 3*60 + 2 + 0.001)
    Timedelta            4:3:2.1                   timedelta(seconds=4*60*60 + 3*60 + 2 + 0.1)
    Timedelta            100:00:00                 timedelta(seconds=100*60*60)
    Timedelta            -00:01                    timedelta(seconds=-1)

Invalid timedelta
    [Template]           Conversion Should Fail
    Timedelta            foobar                                          error=Invalid time string 'foobar'.
    Timedelta            1 foo                                           error=Invalid time string '1 foo'.
    Timedelta            01:02:03:04                                     error=Invalid time string '01:02:03:04'.

List
    List                 []                        []
    List                 ['foo', 'bar']            ${LIST}
    List                 [1, 2, 3.14, -42]         [1, 2, 3.14, -42]
    List                 ['\\x00', '\\x52']        ['\\x00', 'R']

Invalid list
    [Template]           Conversion Should Fail
    List                 [1, ooops]                                      error=Invalid expression.
    List                 ()                                              error=Value is tuple, not list.
    List                 {}                                              error=Value is dictionary, not list.
    List                 ooops                                           error=Invalid expression.
    List                 ${EMPTY}                                        error=Invalid expression.
    List                 !"#¤%&/(inv expr)\=?                            error=Invalid expression.
    List                 1 / 0                                           error=Invalid expression.

Tuple
    Tuple                ()                        ()
    Tuple                ('foo', "bar")            tuple(${LIST})
    Tuple                (1, 2, 3.14, -42)         (1, 2, 3.14, -42)

Invalid tuple
    [Template]           Conversion Should Fail
    Tuple                (1, ooops)                                      error=Invalid expression.
    Tuple                []                                              error=Value is list, not tuple.
    Tuple                {}                                              error=Value is dictionary, not tuple.
    Tuple                ooops                                           error=Invalid expression.

Dictionary
    Dictionary           {}                        {}
    Dict                 {'foo': 1, "bar": 2}      dict(${DICT})
    Map                  {1: 2, 3.14: -42}         {1: 2, 3.14: -42}

Invalid dictionary
    [Template]           Conversion Should Fail
    Dictionary           {1: ooops}                                      error=Invalid expression.
    Dict                 []                        type=dictionary       error=Value is list, not dict.
    Map                  ()                        type=dictionary       error=Value is tuple, not dict.
    Dict                 ooops                     type=dictionary       error=Invalid expression.
    Dictionary           {{'not': 'hashable'}: 'xxx'}                    error=Evaluating expression failed: *

Set
    Set                  set()                     set()
    Set                  {'foo', 'bar'}            {'foo', 'bar'}
    Set                  {1, 2, 3.14, -42}         {1, 2, 3.14, -42}

Invalid set
    [Template]           Conversion Should Fail
    Set                  {1, ooops}                                      error=Invalid expression.
    Set                  {}                                              error=Value is dictionary, not set.
    Set                  ()                                              error=Value is tuple, not set.
    Set                  []                                              error=Value is list, not set.
    Set                  ooops                                           error=Invalid expression.
    Set                  {{'not', 'hashable'}}                           error=Evaluating expression failed: *
    Set                  frozenset()                                     error=Invalid expression.

Frozenset
    Frozenset            frozenset()               frozenset()
    Frozenset            set()                     frozenset()
    Frozenset            {'foo', 'bar'}            frozenset({'foo', 'bar'})
    Frozenset            {1, 2, 3.14, -42}         frozenset({1, 2, 3.14, -42})

Invalid frozenset
    [Template]           Conversion Should Fail
    Frozenset            {1, ooops}                                      error=Invalid expression.
    Frozenset            {}                                              error=Value is dictionary, not set.
    Frozenset            ooops                                           error=Invalid expression.
    Frozenset            {{'not', 'hashable'}}                           error=Evaluating expression failed: *
