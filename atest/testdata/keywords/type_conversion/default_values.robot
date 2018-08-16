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

Float
    Float                1.5                       ${1.5}
    Float                -1                        ${-1.0}
    Float                1e6                       ${1000000.0}
    Float                -1.2e-3                   ${-0.0012}

Decimal
    Decimal              3.14                      Decimal('3.14')
    Decimal              -1                        Decimal('-1')
    Decimal              1e6                       Decimal('1000000')

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

Bytearray
    Bytearray            foo                       bytearray(b'foo')
    Bytearray            \x00\x01\xFF\u00FF        bytearray(b'\\x00\\x01\\xFF\\xFF')
    Bytearray            Hyvä esimerkki!           bytearray(b'Hyv\\xE4 esimerkki!')
    Bytearray            None                      bytearray(b'None')
    Bytearray            NONE                      bytearray(b'NONE')

Datetime
    DateTime             2014-06-11T10:07:42       datetime(2014, 6, 11, 10, 7, 42)
    DateTime             20180808144342123456      datetime(2018, 8, 8, 14, 43, 42, 123456)
    DateTime             1975:06:04                datetime(1975, 6, 4)

Date
    Date                 2014-06-11                date(2014, 6, 11)
    Date                 20180808                  date(2018, 8, 8)
    Date                 20180808000000000000      date(2018, 8, 8)

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

Enum
    [Tags]               require-py3
    Enum                 FOO                       MyEnum.FOO
    Enum                 bar                       MyEnum.bar

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

Tuple
    Tuple                ()                        ()
    Tuple                ('foo', "bar")            tuple(${LIST})
    Tuple                (1, 2, 3.14, -42)         (1, 2, 3.14, -42)

Dictionary
    Dictionary           {}                        {}
    Dictionary           {'foo': 1, "bar": 2}      dict(${DICT})
    Dictionary           {1: 2, 3.14: -42}         {1: 2, 3.14: -42}

Set
    [Tags]               require-py3
    Set                  set()                     set()
    Set                  {'foo', 'bar'}            {'foo', 'bar'}
    Set                  {1, 2, 3.14, -42}         {1, 2, 3.14, -42}

Frozenset
    [Tags]               require-py3
    Frozenset            set()                     frozenset()
    Frozenset            frozenset()               frozenset()
    Frozenset            {'foo', 'bar'}            frozenset({'foo', 'bar'})
    Frozenset            {1, 2, 3.14, -42}         frozenset({1, 2, 3.14, -42})

Sets are not supported in Python 2
    [Tags]               require-py2
    Set                  set()                     u'set()'
    Set                  {'foo', 'bar'}            u"{'foo', 'bar'}"
    Frozenset            set()                     u'set()'
    Frozenset            frozenset()               u'frozenset()'
    Frozenset            {'foo', 'bar'}            u"{'foo', 'bar'}"

Invalid values are passed as-is
    [Template]           Invalid value is passed as-is
    Integer
    Float
    Decimal
    Boolean
    Bytes                extra=\u0100
    Bytearray            extra=\u0100
    Datetime
    Date
    Timedelta
    Enum
    List
    Tuple
    Dictionary
    Set
    Frozenset
    None

Unknown types are not converted
    Unknown              foo                       u'foo'
    Unknown              1                         u'1'
    Unknown              true                      u'true'
    Unknown              None                      u'None'
    Unknown              none                      u'none'
    Unknown              []                        u'[]'

String None is converted to None object
    [Template]           String None is converted to None object
    Integer
    Float
    Decimal
    Boolean
    Datetime
    Date
    Timedelta
    Enum
    List
    Tuple
    Dictionary
    Set
    Frozenset

*** Keywords ***
Invalid value is passed as-is
    [Arguments]    ${kw}    ${extra}=
    Run Keyword    ${kw}    foobar${extra}    u'foobar${extra}'
    Run Keyword    ${kw}    !"#¤%&${extra}    u'!"#¤%&${extra}'
    Run Keyword    ${kw}    [oops]${extra}    u'[oops]${extra}'
    Run Keyword    ${kw}    (o,ps)${extra}    u'(o,ps)${extra}'
    Run Keyword    ${kw}    {o:ps}${extra}    u'{o:ps}${extra}'
    Run Keyword    ${kw}    {oops}${extra}    u'{oops}${extra}'
