*** Settings ***
Library                  Annotations.py
Library                  OperatingSystem
Resource                 conversion.resource

*** Variables ***
@{LIST}                  foo                       bar
&{DICT}                  foo=${1}                  bar=${2}
${FRACTION 1/2}          ${{fractions.Fraction(1,2)}}
${DECIMAL 1/2}           ${{decimal.Decimal('0.5')}}

*** Test Cases ***
Integer
    Integer              42                        42
    Integer              -1                        -1
    Integer              9999999999999999999999    9999999999999999999999
    Integer              123 456 789               123456789
    Integer              123_456_789               123456789
    Integer              - 123 456 789             -123456789
    Integer              -_123_456_789             -123456789
    Integer              ${41}                     41
    Integer              ${-4.0}                   -4

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
    [Template]           Conversion Should Fail
    Integer              foobar
    Integer              1.0
    Integer              0xINVALID
    Integer              0o8
    Integer              0b2
    Integer              00b1
    Integer              0x0x0
    Integer              ${None}                   arg_type=None

Integral (abc)
    Integral             42                        42
    Integral             -1                        -1
    Integral             999_999 999_999 999       999999999999999

Invalid integral (abc)
    [Template]           Conversion Should Fail
    Integral             foobar                    type=integer
    Integral             1.0                       type=integer
    Integral             ${LIST}                   type=integer    arg_type=list

Float
    Float                1.5                       1.5
    Float                -1                        -1.0
    Float                1e6                       1000000.0
    Float                1 000 000 . 0_0_1         1000000.001
    Float                -1.2e-3                   -0.0012
    Float                ${4}                      4.0
    Float                ${-4.1}                   -4.1
    Float                ${FRACTION 1/2}           0.5

Invalid float
    [Template]           Conversion Should Fail
    Float                foobar
    Float                ${LIST}                   arg_type=list

Real (abc)
    Real                 1.5                       1.5
    Real                 -1                        -1.0
    Real                 1e6                       1000000.0
    Real                 1 000 000 . 0_0_1         1000000.001
    Real                 -1.2e-3                   -0.0012
    Real                 ${FRACTION 1/2}           Fraction(1,2)

Invalid real (abc)
    [Template]           Conversion Should Fail
    Real                 foobar                    type=float

Decimal
    Decimal              3.14                      Decimal('3.14')
    Decimal              -1                        Decimal('-1')
    Decimal              1e6                       Decimal('1000000')
    Decimal              1 000 000 . 0_0_1         Decimal('1000000.001')
    Decimal              ${1}                      Decimal(1)
    Decimal              ${1.1}                    Decimal(1.1)
    Decimal              ${DECIMAL 1/2}            Decimal(0.5)

Invalid decimal
    [Template]           Conversion Should Fail
    Decimal              foobar
    Decimal              ${LIST}                   arg_type=list

Boolean
    Boolean              True                      True
    Boolean              YES                       True
    Boolean              on                        True
    Boolean              1                         True
    Boolean              false                     False
    Boolean              No                        False
    Boolean              oFF                       False
    Boolean              0                         False
    Boolean              ${EMPTY}                  False
    Boolean              none                      None
    Boolean              ${1}                      1
    Boolean              ${1.1}                    1.1
    Boolean              ${None}                   None

Invalid boolean string is accepted as-is
    Boolean              FooBar                    'FooBar'
    Boolean              42                        '42'

Invalid boolean
    [Template]           Conversion Should Fail
    Boolean              ${LIST}                   arg_type=list

String
    String               Hello, world!             'Hello, world!'
    String               åäö                       'åäö'
    String               None                      'None'
    String               True                      'True'
    String               []                        '[]'
    String               1.2                       '1.2'
    String               2                         '2'
    String               ${42}                     '42'
    String               ${None}                   'None'
    String               ${LIST}                   "['foo', 'bar']"

Invalid string
    [Template]           Conversion Should Fail
    String               ${{type('Bang', (), {'__str__': lambda self: 1/0})()}}
    ...                  arg_type=Bang             error=ZeroDivisionError: *

Bytes
    Bytes                foo                       b'foo'
    Bytes                \x00\x01\xFF\u00FF        b'\\x00\\x01\\xFF\\xFF'
    Bytes                Hyvä esimerkki!           b'Hyv\\xE4 esimerkki!'
    Bytes                None                      b'None'
    Bytes                NONE                      b'NONE'
    Bytes                ${{b'foo'}}               b'foo'
    Bytes                ${{bytearray(b'foo')}}    b'foo'

Invalid bytes
    [Template]           Conversion Should Fail
    Bytes                \u0100                    error=Character '\u0100' cannot be mapped to a byte.
    Bytes                \u00ff\u0100\u0101        error=Character '\u0100' cannot be mapped to a byte.
    Bytes                Hyvä esimerkki! \u2603    error=Character '\u2603' cannot be mapped to a byte.
    Bytes                ${1.3}                    arg_type=float

Bytestring
    Bytestring           foo                       b'foo'
    Bytestring           \x00\x01\xFF\u00FF        b'\\x00\\x01\\xFF\\xFF'
    Bytestring           Hyvä esimerkki!           b'Hyv\\xE4 esimerkki!'
    Bytestring           None                      b'None'
    Bytestring           NONE                      b'NONE'
    Bytestring           ${{b'foo'}}               b'foo'
    Bytestring           ${{bytearray(b'foo')}}    bytearray(b'foo')

Invalid bytesstring
    [Template]           Conversion Should Fail
    Bytestring           \u0100                    type=bytes            error=Character '\u0100' cannot be mapped to a byte.
    Bytestring           \u00ff\u0100\u0101        type=bytes            error=Character '\u0100' cannot be mapped to a byte.
    Bytestring           Hyvä esimerkki! \u2603    type=bytes            error=Character '\u2603' cannot be mapped to a byte.

Bytearray
    Bytearray            foo                       bytearray(b'foo')
    Bytearray            \x00\x01\xFF\u00FF        bytearray(b'\\x00\\x01\\xFF\\xFF')
    Bytearray            Hyvä esimerkki!           bytearray(b'Hyv\\xE4 esimerkki!')
    Bytearray            None                      bytearray(b'None')
    Bytearray            NONE                      bytearray(b'NONE')
    Bytearray            ${{b'foo'}}               bytearray(b'foo')
    Bytearray            ${{bytearray(b'foo')}}    bytearray(b'foo')

Invalid bytearray
    [Template]           Conversion Should Fail
    Bytearray            \u0100                    error=Character '\u0100' cannot be mapped to a byte.
    Bytearray            \u00ff\u0100\u0101        error=Character '\u0100' cannot be mapped to a byte.
    Bytearray            Hyvä esimerkki! \u2603    error=Character '\u2603' cannot be mapped to a byte.
    Bytearray            ${2123.1021}              arg_type=float

Datetime
    DateTime             2014-06-11T10:07:42       datetime(2014, 6, 11, 10, 7, 42)
    DateTime             20180808144342123456      datetime(2018, 8, 8, 14, 43, 42, 123456)
    DateTime             1975:06:04                datetime(1975, 6, 4)
    DateTime             ${0}                      datetime.fromtimestamp(0)
    DateTime             ${1602232445}             datetime.fromtimestamp(1602232445)
    DateTime             ${0.0}                    datetime.fromtimestamp(0)
    DateTime             ${1612230445.1}           datetime.fromtimestamp(1612230445.1)

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
    Date                 ${123}                                          arg_type=integer
    Date                 ${12.3}                                         arg_type=float

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
    Timedelta            ${21}                     timedelta(seconds=21)
    Timedelta            ${2.1}                    timedelta(seconds=2.1)
    Timedelta            ${-2.1}                   timedelta(seconds=-2.1)

Invalid timedelta
    [Template]           Conversion Should Fail
    Timedelta            foobar                    error=Invalid time string 'foobar'.
    Timedelta            1 foo                     error=Invalid time string '1 foo'.
    Timedelta            01:02:03:04               error=Invalid time string '01:02:03:04'.
    Timedelta            ${LIST}                   arg_type=list

Enum
    Enum                 FOO                       MyEnum.FOO
    Enum                 bar                       MyEnum.bar
    Enum                 foo                       MyEnum.foo
    None enum            NTWO                      NoneEnum.NTWO
    None enum            None                      NoneEnum.NONE
    None enum            NONE                      NoneEnum.NONE

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

Normalized enum member match
    Enum                 b a r                     MyEnum.bar
    Enum                 BAr                       MyEnum.bar
    Enum                 B_A_r                     MyEnum.bar
    Enum                 normalize_me              MyEnum.normalize_me
    Enum                 normalize me              MyEnum.normalize_me
    Enum                 Normalize Me              MyEnum.normalize_me
    Flag                 red                       MyFlag.RED
    IntEnum              on                        MyIntEnum.ON
    IntFlag              x                         MyIntFlag.X

Normalized enum member match with multiple matches
    [Template]           Conversion Should Fail
    Enum                 Foo                       type=MyEnum           error=MyEnum has multiple members matching 'Foo'. Available: 'FOO' and 'foo'

Invalid Enum
    [Template]           Conversion Should Fail
    Enum                 foobar                    type=MyEnum           error=MyEnum does not have member 'foobar'. Available: 'FOO', 'bar', 'foo' and 'normalize_me'
    Enum                 bar!                      type=MyEnum           error=MyEnum does not have member 'bar!'. Available: 'FOO', 'bar', 'foo' and 'normalize_me'
    Enum                 None                      type=MyEnum           error=MyEnum does not have member 'None'. Available: 'FOO', 'bar', 'foo' and 'normalize_me'
    Enum                 1                         type=MyEnum           error=MyEnum does not have member '1'. Available: 'FOO', 'bar', 'foo' and 'normalize_me'
    Flag                 foobar                    type=MyFlag           error=MyFlag does not have member 'foobar'. Available: 'BLUE' and 'RED'

Invalid IntEnum
    [Template]           Conversion Should Fail
    IntEnum              nonex                     type=MyIntEnum        error=MyIntEnum does not have member 'nonex'. Available: 'OFF (0)' and 'ON (1)'
    IntEnum              2                         type=MyIntEnum        error=MyIntEnum does not have member '2'. Available: 'OFF (0)' and 'ON (1)'
    IntEnum              ${2}                      type=MyIntEnum        error=MyIntEnum does not have value '2'. Available: '0' and '1'          arg_type=integer
    IntFlag              3                         type=MyIntFlag        error=MyIntFlag does not have member '3'. Available: 'R (4)', 'W (2)' and 'X (1)'
    IntFlag              ${-1}                     type=MyIntFlag        error=MyIntFlag does not have value '-1'. Available: '1', '2' and '4'    arg_type=integer

NoneType
    NoneType             None                      None
    NoneType             NONE                      None

Invalid NoneType
    [Template]           Conversion Should Fail
    NoneType             Hello, world!             type=None
    NoneType             True                      type=None
    NoneType             []                        type=None

List
    List                 []                        []
    List                 ['foo', 'bar']            ${LIST}
    List                 [1, 2, 3.14, -42]         [1, 2, 3.14, -42]
    List                 ['\\x00', '\\x52']        ['\\x00', 'R']
    List                 [{'nested': True}]        [{'nested': True}]
    List                 ${{[1, 2]}}               [1, 2]
    List                 ${{(1, 2)}}               [1, 2]

Invalid list
    [Template]           Conversion Should Fail
    List                 [1, ooops]                error=Invalid expression.
    List                 ()                        error=Value is tuple, not list.
    List                 {}                        error=Value is dictionary, not list.
    List                 ooops                     error=Invalid expression.
    List                 ${EMPTY}                  error=Invalid expression.
    List                 !"#¤%&/(inv expr)\=?      error=Invalid expression.
    List                 1 / 0                     error=Invalid expression.
    List                 ${NONE}                   arg_type=None

Sequence (abc)
    Sequence             []                        []
    Sequence             ['foo', 'bar']            ${LIST}
    Mutable sequence     [1, 2, 3.14, -42]         [1, 2, 3.14, -42]
    Mutable sequence     ['\\x00', '\\x52']        ['\\x00', 'R']

Invalid sequence (abc)
    [Template]           Conversion Should Fail
    Sequence             [1, ooops]                type=list             error=Invalid expression.
    Mutable sequence     ()                        type=list             error=Value is tuple, not list.
    Sequence             {}                        type=list             error=Value is dictionary, not list.
    Mutable sequence     ooops                     type=list             error=Invalid expression.
    Sequence             ${EMPTY}                  type=list             error=Invalid expression.
    Mutable sequence     !"#¤%&/(inv expr)\=?      type=list             error=Invalid expression.
    Sequence             1 / 0                     type=list             error=Invalid expression.

Tuple
    Tuple                ()                        ()
    Tuple                ('foo', "bar")            tuple(${LIST})
    Tuple                (1, 2, 3.14, -42)         (1, 2, 3.14, -42)
    Tuple                (['nested', True],)       (['nested', True],)
    Tuple                ${{(1, 2)}}               (1, 2)
    Tuple                ${{[1, 2]}}               (1, 2)

Invalid tuple
    [Template]           Conversion Should Fail
    Tuple                (1, ooops)                error=Invalid expression.
    Tuple                []                        error=Value is list, not tuple.
    Tuple                {}                        error=Value is dictionary, not tuple.
    Tuple                ooops                     error=Invalid expression.
    Tuple                ${NONE}                   arg_type=None

Dictionary
    Dictionary           {}                        {}
    Dictionary           {'foo': 1, "bar": 2}      dict(${DICT})
    Dictionary           {1: 2, 3.14: -42}         {1: 2, 3.14: -42}

Invalid dictionary
    [Template]           Conversion Should Fail
    Dictionary           {1: ooops}                                      error=Invalid expression.
    Dictionary           []                                              error=Value is list, not dict.
    Dictionary           ()                                              error=Value is tuple, not dict.
    Dictionary           ooops                                           error=Invalid expression.
    Dictionary           {{'not': 'hashable'}: 'xxx'}                    error=Evaluating expression failed: *
    Dictionary           ${NONE}                                         arg_type=None

Mapping (abc)
    Mapping              {'foo': 1, 2: 'bar'}      {'foo': 1, 2: 'bar'}
    Mutable mapping      {'foo': 1, 2: 'bar'}      {'foo': 1, 2: 'bar'}

Invalid mapping (abc)
    [Template]           Conversion Should Fail
    Mapping              foobar                    type=dictionary       error=Invalid expression.
    Mapping              []                        type=dictionary       error=Value is list, not dict.
    Mutable mapping      barfoo                    type=dictionary       error=Invalid expression.

Set
    Set                  set()                     set()
    Set                  {'foo', 'bar'}            {'foo', 'bar'}
    Set                  {1, 2, 3.14, -42}         {1, 2, 3.14, -42}
    Set                  ${{{1}}}                  {1}
    Set                  ${{frozenset({1})}}       {1}
    Set                  ${{[1]}}                  {1}
    Set                  ${{(1,)}}                 {1}
    Set                  ${{{1: 2}}}               {1}

Invalid set
    [Template]           Conversion Should Fail
    Set                  {1, ooops}                error=Invalid expression.
    Set                  {}                        error=Value is dictionary, not set.
    Set                  ()                        error=Value is tuple, not set.
    Set                  []                        error=Value is list, not set.
    Set                  ooops                     error=Invalid expression.
    Set                  {{'not', 'hashable'}}     error=Evaluating expression failed: *
    Set                  frozenset()               error=Invalid expression.
    Set                  ${NONE}                   arg_type=None

Set (abc)
    Set abc              set()                     set()
    Set abc              {'foo', 'bar'}            {'foo', 'bar'}
    Set abc              {1, 2, 3.14, -42}         {1, 2, 3.14, -42}
    Mutable set          set()                     set()
    Mutable set          {'foo', 'bar'}            {'foo', 'bar'}
    Mutable set          {1, 2, 3.14, -42}         {1, 2, 3.14, -42}

Invalid set (abc)
    [Template]           Conversion Should Fail
    Set abc              {1, ooops}                type=set              error=Invalid expression.
    Set abc              {}                        type=set              error=Value is dictionary, not set.
    Set abc              ooops                     type=set              error=Invalid expression.
    Mutable set          {1, ooops}                type=set              error=Invalid expression.
    Mutable set          {}                        type=set              error=Value is dictionary, not set.
    Mutable set          ooops                     type=set              error=Invalid expression.

Frozenset
    Frozenset            frozenset()               frozenset()
    Frozenset            set()                     frozenset()
    Frozenset            {'foo', 'bar'}            frozenset({'foo', 'bar'})
    Frozenset            {1, 2, 3.14, -42}         frozenset({1, 2, 3.14, -42})
    Frozenset            ${{frozenset({1})}}       frozenset({1})
    Frozenset            ${{{1}}}                  frozenset({1})
    Frozenset            ${{[1]}}                  frozenset({1})
    Frozenset            ${{(1,)}}                 frozenset({1})
    Frozenset            ${{{1: 2}}}               frozenset({1})

Invalid frozenset
    [Template]           Conversion Should Fail
    Frozenset            {1, ooops}                error=Invalid expression.
    Frozenset            {}                        error=Value is dictionary, not set.
    Frozenset            ooops                     error=Invalid expression.
    Frozenset            {{'not', 'hashable'}}     error=Evaluating expression failed: *

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
    Invalid              foo                       'foo'
    Invalid              1                         '1'
    Invalid              true                      'true'
    Invalid              None                      'None'
    Invalid              none                      'none'
    Invalid              []                        '[]'

Positional as named
    Integer              argument=-1               expected=-1
    Float                argument=1e2              expected=100.0
    Dictionary           argument={'a': 1}         expected={'a': 1}

Invalid positional as named
    [Template]           Conversion Should Fail
    Integer              argument=1.0
    Float                argument=xxx
    Dictionary           argument=[0]                                    error=Value is list, not dict.

Varargs
    Varargs              1    2    3               expected=(1, 2, 3)
    Varargs              ${1}    ${2.0}            expected=(1, 2)

Invalid varargs
    [Template]           Conversion Should Fail
    Varargs              foobar                    type=integer
    Varargs              ${NONE}                   type=integer    arg_type=None

Kwargs
    Kwargs               a=1    b=2    c=3         expected={'a': 1, 'b': 2, 'c': 3}
    Kwargs               a=${1}    b=${2.0}        expected={'a': 1, 'b': 2}

Invalid Kwargs
    [Template]           Conversion Should Fail
    Kwargs               kwarg=ooops               type=integer
    Kwargs               kwarg=${1.2}              type=integer    arg_type=float    error=Conversion would lose precision.

Kwonly
    Kwonly               argument=1.0              expected=1.0
    Kwonly               argument=${1}             expected=1.0

Invalid kwonly
    [Template]           Conversion Should Fail
    Kwonly               argument=foobar           type=float
    Kwonly               argument=${NONE}          type=float    arg_type=None

Return value annotation causes no error
    Return value annotation                    42    42

None as default
    None as default
    None as default                            []    []

Forward references
    [Tags]    require-py3.5
    Forward referenced concrete type           42    42
    Forward referenced ABC                     []    []

@keyword decorator overrides annotations
    Types via keyword deco override            42    timedelta(seconds=42)
    None as types via @keyword disables        42    '42'
    Empty types via @keyword doesn't override  42    42
    @keyword without types doesn't override    42    42

Type information mismatch caused by decorator
    Mismatch caused by decorator               foo   'foo'

Decorator with wraps
    Keyword With Wraps                         42    42

Decorator with wraps mismatched type
    Conversion Should Fail
    ...    Keyword With Wraps    argument=foobar    type=integer

Value contains variable
    [Setup]       Set Environment Variable         PI_NUMBER    3.14
    [Teardown]    Remove Environment Variable      PI_NUMBER
    Float                %{PI_NUMBER}              ${3.14}
    ${value} =           Set variable              42
    Integer              ${value}                  ${42}
    @{value} =           Create List               1    2    3
    Varargs              @{value}                  expected=(1, 2, 3)
    &{value} =           Create Dictionary         a=1    b=2    c=3
    Kwargs               &{value}                  expected={'a': 1, 'b': 2, 'c': 3}

Default value is not used if explicit type conversion succeeds
    Type and default 1    [1, 2]    [1, 2]
    Type and default 2    42        42

Default value is used if explicit type conversion fails
    Type and default 1    none       None
    Type and default 2    FALSE      False
    Type and default 2    ok also    'ok also'
    Type and default 3    10         ${{datetime.timedelta(seconds=10)}}

Explicit conversion failure is used if both conversions fail
    [Template]    Conversion Should Fail
    Type and default 4    BANG!    type=list         error=Invalid expression.
    Type and default 3    BANG!    type=timedelta    error=Invalid time string 'BANG!'.
