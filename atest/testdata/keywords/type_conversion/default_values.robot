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
    Integer              123 456 789               123456789
    Integer              123_456_789               123456789
    Integer              - 123 456 789             -123456789
    Integer              -_123_456_789             -123456789

Integer as float
    Integer              1.0                       ${1.0}
    Integer              1.5                       ${1.5}

Integer as hex
    Integer              0x0                        0
    Integer              0 X 0 0 0 0 0              0
    Integer              0_X_0_0_0_0_0              0
    Integer              0x1000                     4096
    Integer              -0x1000                    -4096
    Integer              +0x1000                    4096
    Integer              0x00FF                     255
    Integer              - 0 X 00 ff                -255
    Integer              -__0__X__00_ff__           -255
    Integer              0 x BAD C0FFEE             50159747054

Integer as octal
    Integer              0o0                        0
    Integer              0 O 0 0 0 0 0              0
    Integer              0_O_0_0_0_0_0              0
    Integer              0o1000                     512
    Integer              -0o1000                    -512
    Integer              +0o1000                    512
    Integer              0o0077                     63
    Integer              - 0 o 00 77                -63
    Integer              -__0__o__00_77__           -63

Integer as binary
    Integer              0b0                        0
    Integer              0 B 0 0 0 0 0              0
    Integer              0_B_0_0_0_0_0              0
    Integer              0b1000                     8
    Integer              -0b1000                    -8
    Integer              +0b1000                    8
    Integer              0b0011                     3
    Integer              - 0 b 00 11                -3
    Integer              -__0__b__00_11__           -3

Invalid integer
    [Template]           Invalid value is passed as-is
    Integer              foobar
    Integer              0xFOOBAR
    Integer              0o8
    Integer              0b2
    Integer              00b1
    Integer              0x0x0

Float
    Float                1.5                       ${1.5}
    Float                -1                        ${-1.0}
    Float                1e6                       ${1000000.0}
    Float                1 000 000 . 0_0_1         1000000.001
    Float                -1.2e-3                   ${-0.0012}

Invalid float
    [Template]           Invalid value is passed as-is
    Float                foobar

Decimal
    Decimal              3.14                      Decimal('3.14')
    Decimal              -1                        Decimal('-1')
    Decimal              1e6                       Decimal('1000000')
    Decimal              1 000 000 . 0_0_1         Decimal('1000000.001')

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
    Boolean              none                      ${None}
    Boolean              ${None}                   ${None}
    Boolean              ${0}                      ${0}
    Boolean              ${1.1}                    ${1.1}

Invalid boolean
    [Template]           Invalid value is passed as-is
    Boolean              foobar
    Boolean              ${LIST}                   expected=${LIST}

String
    String               Hello, world!             u'Hello, world!'
    String               åäö                       u'åäö'
    String               None                      u'None'
    String               True                      u'True'
    String               []                        u'[]'
    String               ${42}                     42
    String               ${None}                   None
    String               ${LIST}                   ['foo', 'bar']

Bytes
    Bytes                foo                       b'foo'
    Bytes                \x00\x01\xFF\u00FF        b'\\x00\\x01\\xFF\\xFF'
    Bytes                Hyvä esimerkki!           b'Hyv\\xE4 esimerkki!'
    Bytes                None                      b'None'
    Bytes                NONE                      b'NONE'

Invalid bytes
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
    Enum                 FOO                       MyEnum.FOO
    Enum                 bar                       MyEnum.bar

Flag
    Flag                 RED                       MyFlag.RED

IntEnum
    IntEnum              ON                        MyIntEnum.ON
    IntEnum              ${1}                      MyIntEnum.ON
    IntEnum              0                         MyIntEnum.OFF

IntFlag
    IntFlag              R                         MyIntFlag.R
    IntFlag              4                         MyIntFlag.R
    IntFlag              ${4}                      MyIntFlag.R

Invalid enum
    [Template]           Invalid value is passed as-is
    Enum                 foobar
    Flag                 YELLOW
    IntEnum              -1
    IntFlag              ${10}                     ${10}

None
    None                 None                      None
    None                 NONE                      None
    None                 Hello, world!             'Hello, world!'
    None                 True                      'True'
    None                 []                        '[]'

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

Unknown types are not converted
    Unknown              foo                       'foo'
    Unknown              1                         '1'
    Unknown              true                      'true'
    Unknown              None                      'None'
    Unknown              none                      'none'
    Unknown              []                        '[]'

Positional as named
    Integer              argument=-1               expected=-1
    Float                argument=1e2              expected=100.0
    Dictionary           argument={'a': 1}         expected={'a': 1}

Invalid positional as named
    Integer              argument=1.0              expected=1.0
    Float                argument=xxx              expected='xxx'
    Dictionary           argument=[0]              expected='[0]'

Kwonly
    Kwonly               argument=1.0              expected=1.0

Invalid kwonly
    Kwonly               argument=foobar           expected='foobar'

@keyword decorator overrides default values
    Types via keyword deco override            42    timedelta(seconds=42)
    None as types via @keyword disables        42    '42'
    Empty types via @keyword doesn't override  42    42
    @keyword without types doesn't override    42    42

*** Keywords ***
Invalid value is passed as-is
    [Arguments]    ${kw}    ${arg}    ${expected}='''${arg}'''
    Run Keyword    ${kw}    ${arg}    ${expected}
