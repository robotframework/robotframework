*** Settings ***
Library                  KeywordDecorator.py
Resource                 conversion.resource

*** Variables ***
@{LIST}                  foo                       bar
&{DICT}                  foo=${1}                  bar=${2}

*** Test Cases ***
Integer
    Integer              42                        ${42}
    Integer              -1                        ${-1}
    Integer              9999999999999999999999    ${9999999999999999999999}

Invalid integer
    [Template]           Conversion Should Fail
    Integer              foobar
    Integer              1.0

Float
    Float                1.5                       ${1.5}
    Float                -1                        ${-1.0}
    Float                1e6                       ${1000000.0}
    Float                -1.2e-3                   ${-0.0012}

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
    Boolean              YES                       ${True}
    Boolean              on                        ${True}
    Boolean              1                         ${True}
    Boolean              false                     ${False}
    Boolean              No                        ${False}
    Boolean              oFF                       ${False}
    Boolean              0                         ${False}
    Boolean              ${EMPTY}                  ${False}
    Boolean              none                      ${None}

Invalid boolean is accepted as-is
    Boolean              FooBar                    'FooBar'
    Boolean              42                        '42'

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
    Bytes                \u0100

Bytearray
    Bytearray            foo                       bytearray(b'foo')
    Bytearray            \x00\x01\xFF\u00FF        bytearray(b'\\x00\\x01\\xFF\\xFF')
    Bytearray            Hyvä esimerkki!           bytearray(b'Hyv\\xE4 esimerkki!')
    Bytearray            None                      bytearray(b'None')
    Bytearray            NONE                      bytearray(b'NONE')

Invalid bytearray
    [Template]           Conversion Should Fail
    Bytearray            \u0100

Datetime
    DateTime             2014-06-11T10:07:42       datetime(2014, 6, 11, 10, 7, 42)
    DateTime             20180808144342123456      datetime(2018, 8, 8, 14, 43, 42, 123456)
    DateTime             1975:06:04                datetime(1975, 6, 4)

Invalid datetime
    [Template]           Conversion Should Fail
    DateTime             foobar
    DateTime             1975:06
    DateTime             2018
    DateTime             201808081443421234567

Date
    Date                 2014-06-11                date(2014, 6, 11)
    Date                 20180808                  date(2018, 8, 8)
    Date                 20180808000000000000      date(2018, 8, 8)

Invalid date
    [Template]           Conversion Should Fail
    Date                 foobar
    Date                 1975:06
    Date                 2018
    Date                 2014-06-11T10:07:42
    Date                 20180808000000000001

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
    Timedelta            foobar
    Timedelta            1 foo
    Timedelta            01:02:03:04

Enum
    [Tags]               require-enum
    Enum                 FOO                       MyEnum.FOO
    Enum                 bar                       MyEnum.bar

Invalid Enum
    [Tags]               require-enum
    [Template]           Conversion Should Fail
    Enum                 foobar                    type=MyEnum
    Enum                 BAR                       type=MyEnum

NoneType
    NoneType             None                      None
    NoneType             NONE                      None
    NoneType             Hello, world!             'Hello, world!'
    NoneType             True                      'True'
    NoneType             []                        '[]'

List
    List                 []                        []
    List                 ['foo', 'bar']            ${LIST}
    List                 [1, 2, 3.14, -42]         [1, 2, 3.14, -42]
    List                 ['\\x00', '\\x52']        ['\\x00', 'R']

Invalid list
    [Template]           Conversion Should Fail
    List                 [1, ooops]
    List                 ()
    List                 {}
    List                 ooops
    List                 ${EMPTY}
    List                 !"#¤%&/(invalid expression)\=?
    List                 1 / 0

Tuple
    Tuple                ()                        ()
    Tuple                ('foo', "bar")            tuple(${LIST})
    Tuple                (1, 2, 3.14, -42)         (1, 2, 3.14, -42)

Invalid tuple
    [Template]           Conversion Should Fail
    Tuple                (1, ooops)
    Tuple                []
    Tuple                {}
    Tuple                ooops

Dictionary
    Dictionary           {}                        {}
    Dictionary           {'foo': 1, "bar": 2}      dict(${DICT})
    Dictionary           {1: 2, 3.14: -42}         {1: 2, 3.14: -42}

Invalid dictionary
    [Template]           Conversion Should Fail
    Dictionary           {1: ooops}
    Dictionary           []
    Dictionary           ()
    Dictionary           ooops
    Dictionary           {{'not': 'hashable'}: 'xxx'}

Set
    [Tags]               require-py3
    Set                  set()                     set()
    Set                  {'foo', 'bar'}            {'foo', 'bar'}
    Set                  {1, 2, 3.14, -42}         {1, 2, 3.14, -42}

Invalid set
    [Template]           Conversion Should Fail
    Set                  {1, ooops}
    Set                  {}
    Set                  ()
    Set                  []
    Set                  ooops
    Set                  {{'not', 'hashable'}}
    Set                  frozenset()

Frozenset
    [Tags]               require-py3
    Frozenset            frozenset()               frozenset()
    Frozenset            set()                     frozenset()
    Frozenset            {'foo', 'bar'}            frozenset({'foo', 'bar'})
    Frozenset            {1, 2, 3.14, -42}         frozenset({1, 2, 3.14, -42})

Invalid frozenset
    [Template]           Conversion Should Fail
    Frozenset            {1, ooops}                type=set
    Frozenset            {}                        type=set
    Frozenset            ooops                     type=set
    Frozenset            {{'not', 'hashable'}}     type=set

Sets are not supported in Python 2
    [Tags]               require-py2
    [Template]           Conversion Should Fail
    Set                  set()
    Set                  {'foo', 'bar'}
    Frozenset            set()                     type=set
    Frozenset            frozenset()               type=set
    Frozenset            {'foo', 'bar'}            type=set

Iterable abc
    Iterable             ['list', 'is', 'ok']      ['list', 'is', 'ok']
    Iterable             ('tuple',)                ('tuple',)
    Iterable             {'dict': 'accepted'}      {'dict': 'accepted'}

Invalid iterable abc
    [Template]           Conversion Should Fail
    Iterable             foobar

Mapping abc
    Mapping              {'foo': 1, 2: 'bar'}      {'foo': 1, 2: 'bar'}
    Mutable mapping      {'foo': 1, 2: 'bar'}      {'foo': 1, 2: 'bar'}

Invalid mapping abc
    [Template]           Conversion Should Fail
    Mapping              foobar                    type=dictionary
    Mapping              []                        type=dictionary
    Mutable mapping      barfoo                    type=dictionary

Set abc
    [Tags]               require-py3
    Set abc              set()                     set()
    Set abc              {'foo', 'bar'}            {'foo', 'bar'}
    Set abc              {1, 2, 3.14, -42}         {1, 2, 3.14, -42}
    Mutable set          set()                     set()
    Mutable set          {'foo', 'bar'}            {'foo', 'bar'}
    Mutable set          {1, 2, 3.14, -42}         {1, 2, 3.14, -42}

Invalid set abc
    [Template]           Conversion Should Fail
    Set abc              {1, ooops}                type=set
    Set abc              {}                        type=set
    Set abc              ooops                     type=set
    Mutable set          {1, ooops}                type=set
    Mutable set          {}                        type=set
    Mutable set          ooops                     type=set

Unknown types are not converted
    Unknown              foo                       'foo'
    Unknown              1                         '1'
    Unknown              true                      'true'
    Unknown              None                      'None'
    Unknown              none                      'none'
    Unknown              []                        '[]'

Non-type values don't cause errors
    Non type             foo                       'foo'
    Non type             1                         '1'
    Non type             true                      'true'
    Non type             None                      'None'
    Non type             none                      'none'
    Non type             []                        '[]'

Positional as named
    Integer              argument=-1               expected=-1
    Float                argument=1e2              expected=100.0
    Dictionary           argument={'a': 1}         expected={'a': 1}

Invalid positional as named
    [Template]           Conversion Should Fail
    Integer              argument=1.0
    Float                argument=xxx
    Dictionary           argument=[0]

Varargs
    Varargs              1    2    3               expected=(1, 2, 3)
    Varargs              ${TRUE}    ${NONE}        expected=(True, None)

Invalid varargs
    [Template]           Conversion Should Fail
    Varargs              foobar                    type=integer

Kwargs
    Kwargs               a=1    b=2    c=3         expected={'a': 1, 'b': 2, 'c': 3}
    Kwargs               x=${TRUE}    y=${NONE}    expected={'x': True, 'y': None}

Invalid Kwargs
    [Template]           Conversion Should Fail
    Kwargs               kwarg=ooops               type=integer

Kwonly
    [Tags]               require-py3
    Kwonly               argument=1.0              expected=1.0

Invalid kwonly
    [Tags]               require-py3
    [Template]           Conversion Should Fail
    Kwonly               argument=foobar           type=float

Non-strings are not converted
    [Template]           Non-string is not converted
    Integer
    Float
    Boolean
    Decimal
    List
    Tuple
    Dictionary
    Set
    Frozenset
    Enum
    Bytes
    Bytearray
    DateTime
    Date
    Timedelta
    NoneType

String None is converted to None object
    [Template]           String None is converted to None object
    Integer
    Float
    Boolean
    Decimal
    List
    Tuple
    Dictionary
    Set
    Frozenset
    DateTime
    Date
    Timedelta

Invalid type spec causes error
    [Documentation]    FAIL No keyword with name 'Invalid type spec' found.
    Invalid type spec

Non-matching argument name causes error
    [Documentation]    FAIL No keyword with name 'Non matching name' found.
    Non matching name

Type can be given to `return` without an error
    Return type          42                        42
