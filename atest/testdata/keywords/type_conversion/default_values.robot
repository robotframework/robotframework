*** Settings ***
Library                  DefaultValues.py
Resource                 conversion.resource

*** Variables ***
@{LIST}                  foo                       bar
&{DICT}                  foo=${1}                  bar=${2}

*** Test Cases ***
Integer
    Integer              42                        ${42}
    Integer              -1                        ${-1}
    Integer              9999999999999999999999    ${9999999999999999999999}

Integer as float
    Integer              1.0                       ${1.0}
    Integer              1.5                       ${1.5}

Invalid integer
    [Template]           Invalid value is passed as-is
    Integer              foobar

Float
    Float                1.5                       ${1.5}
    Float                -1                        ${-1.0}
    Float                1e6                       ${1000000.0}
    Float                -1.2e-3                   ${-0.0012}

Invalid float
    [Template]           Invalid value is passed as-is
    Float                foobar

Decimal
    Decimal              3.14                      Decimal('3.14')
    Decimal              -1                        Decimal('-1')
    Decimal              1e6                       Decimal('1000000')

Invalid decimal
    [Template]           Invalid value is passed as-is
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
    Boolean              none                      ${False}
    Boolean              ${0}                      ${False}
    Boolean              ${1}                      ${True}

Invalid boolean
    [Template]           Invalid value is passed as-is
    Boolean              foobar

String
    String               Hello, world!             u'Hello, world!'
    String               åäö                       u'åäö'
    String               None                      u'None'
    String               True                      u'True'
    String               []                        u'[]'
    Unicode              Hello, world!             u'Hello, world!'
    Unicode              åäö                       u'åäö'
    Unicode              None                      u'None'
    Unicode              True                      u'True'
    Unicode              []                        u'[]'

Bytes
    [Tags]               require-py3
    Bytes                foo                       b'foo'
    Bytes                \x00\x01\xFF\u00FF        b'\\x00\\x01\\xFF\\xFF'
    Bytes                Hyvä esimerkki!           b'Hyv\\xE4 esimerkki!'
    Bytes                None                      b'None'
    Bytes                NONE                      b'NONE'

Invalid bytes
    [Tags]               require-py3
    [Template]           Invalid value is passed as-is
    Bytes                \u0100

Bytearray
    Bytearray            foo                       bytearray(b'foo')
    Bytearray            \x00\x01\xFF\u00FF        bytearray(b'\\x00\\x01\\xFF\\xFF')
    Bytearray            Hyvä esimerkki!           bytearray(b'Hyv\\xE4 esimerkki!')
    Bytearray            None                      bytearray(b'None')
    Bytearray            NONE                      bytearray(b'NONE')

Invalid bytearray
    [Template]           Invalid value is passed as-is
    Bytearray            \u0100

Datetime
    DateTime             2014-06-11T10:07:42       datetime(2014, 6, 11, 10, 7, 42)
    DateTime             20180808144342123456      datetime(2018, 8, 8, 14, 43, 42, 123456)
    DateTime             1975:06:04                datetime(1975, 6, 4)

Invalid datetime
    [Template]           Invalid value is passed as-is
    DateTime             foobar
    DateTime             1975:06

Date
    Date                 2014-06-11                date(2014, 6, 11)
    Date                 20180808                  date(2018, 8, 8)
    Date                 20180808000000000000      date(2018, 8, 8)

Invalid date
    [Template]           Invalid value is passed as-is
    Date                 foobar
    Date                 1975:06
    Date                 2018:08:20 22:22

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
    [Template]           Invalid value is passed as-is
    Timedelta            foobar
    Timedelta            01:02:03:04

Enum
    [Tags]               require-enum
    Enum                 FOO                       MyEnum.FOO
    Enum                 bar                       MyEnum.bar

Invalid enum
    [Template]           Invalid value is passed as-is
    Enum                 foobar

None
    None                 None                      None
    None                 NONE                      None
    None                 Hello, world!             u'Hello, world!'
    None                 True                      u'True'
    None                 []                        u'[]'

List
    List                 []                        []
    List                 ['foo', 'bar']            ${LIST}
    List                 [1, 2, 3.14, -42]         [1, 2, 3.14, -42]
    List                 ['\\x00', '\\x52']        ['\\x00', 'R']

Invalid list
    [Template]           Invalid value is passed as-is
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
    [Template]           Invalid value is passed as-is
    Tuple                (1, ooops)
    Tuple                []
    Tuple                {}
    Tuple                ooops

Dictionary
    Dictionary           {}                        {}
    Dictionary           {'foo': 1, "bar": 2}      dict(${DICT})
    Dictionary           {1: 2, 3.14: -42}         {1: 2, 3.14: -42}

Invalid dictionary
    [Template]           Invalid value is passed as-is
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
    [Template]           Invalid value is passed as-is
    Set                  {1, ooops}
    Set                  {}
    Set                  ()
    Set                  []
    Set                  ooops
    Set                  {{'not', 'hashable'}}
    Set                  frozenset()

Frozenset
    [Tags]               require-py3
    Frozenset            set()                     frozenset()
    Frozenset            frozenset()               frozenset()
    Frozenset            {'foo', 'bar'}            frozenset({'foo', 'bar'})
    Frozenset            {1, 2, 3.14, -42}         frozenset({1, 2, 3.14, -42})

Invalid frozenset
    [Template]           Invalid value is passed as-is
    Frozenset            {1, ooops}
    Frozenset            {}
    Frozenset            ooops
    Frozenset            {{'not', 'hashable'}}

Sets are not supported in Python 2
    [Tags]               require-py2
    Set                  set()                     u'set()'
    Set                  {'foo', 'bar'}            u"{'foo', 'bar'}"
    Frozenset            set()                     u'set()'
    Frozenset            frozenset()               u'frozenset()'
    Frozenset            {'foo', 'bar'}            u"{'foo', 'bar'}"

Unknown types are not converted
    Unknown              foo                       u'foo'
    Unknown              1                         u'1'
    Unknown              true                      u'true'
    Unknown              None                      u'None'
    Unknown              none                      u'none'
    Unknown              []                        u'[]'

Positional as named
    Integer              argument=-1               expected=-1
    Float                argument=1e2              expected=100.0
    Dictionary           argument={'a': 1}         expected={'a': 1}

Invalid positional as named
    Integer              argument=1.0              expected=1.0
    Float                argument=xxx              expected=u'xxx'
    Dictionary           argument=[0]              expected=u'[0]'

Kwonly
    [Tags]               require-py3
    Kwonly               argument=1.0              expected=1.0

Invalid kwonly
    [Tags]               require-py3
    Kwonly               argument=foobar           expected='foobar'

@keyword decorator overrides default values
    Types via keyword deco override            42    timedelta(seconds=42)
    None as types via @keyword disables        42    u'42'
    Empty types via @keyword doesn't override  42    42
    @keyword without types doesn't override    42    42

*** Keywords ***
Invalid value is passed as-is
    [Arguments]    ${kw}    ${arg}
    Run Keyword    ${kw}    ${arg}    u'''${arg}'''
