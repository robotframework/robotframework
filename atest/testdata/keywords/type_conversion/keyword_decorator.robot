*** Settings ***
Library                  KeywordDecorator.py
Library                  OperatingSystem
Resource                 conversion.resource

*** Variables ***
@{LIST}                  foo                       bar
&{DICT}                  foo=${1}                  bar=${2}
${u}                     ${{'u' if sys.version_info[0] == 2 else ''}}

*** Test Cases ***
Integer
    Integer              42                        ${42}
    Integer              -1                        ${-1}
    Integer              9999999999999999999999    ${9999999999999999999999}
    Integer              ${41}                     ${41}
    Integer              ${-4.0}                   ${-4}

Invalid integer
    [Template]           Conversion Should Fail
    Integer              foobar
    Integer              1.0
    Integer              ${None}                   arg_type=None

Integral (abc)
    Integral             42                        ${42}
    Integral             -1                        ${-1}
    Integral             9999999999999999999999    ${9999999999999999999999}

Invalid integral (abc)
    [Template]           Conversion Should Fail
    Integral             foobar                    type=integer
    Integral             1.0                       type=integer
    Integral             ${LIST}                   type=integer    arg_type=list

Float
    Float                1.5                       ${1.5}
    Float                -1                        ${-1.0}
    Float                1e6                       ${1000000.0}
    Float                -1.2e-3                   ${-0.0012}
    Float                ${4}                      ${4.0}
    Float                ${-4.1}                   ${-4.1}

Invalid float
    [Template]           Conversion Should Fail
    Float                foobar
    Float                ${LIST}                   arg_type=list

Real (abc)
    Real                 1.5                       ${1.5}
    Real                 -1                        ${-1.0}
    Real                 1e6                       ${1000000.0}
    Real                 -1.2e-3                   ${-0.0012}

Invalid real (abc)
    [Template]           Conversion Should Fail
    Real                 foobar                    type=float

Decimal
    Decimal              3.14                      Decimal('3.14')
    Decimal              -1                        Decimal('-1')
    Decimal              1e6                       Decimal('1000000')
    Decimal              ${1}                      Decimal(1)
    Decimal              ${1.1}                    Decimal(1.1)

Invalid decimal
    [Template]           Conversion Should Fail
    Decimal              foobar
    Decimal              ${LIST}                   arg_type=list

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
    Boolean              none                      ${NONE}
    Boolean              ${1}                      ${1}
    Boolean              ${1.1}                    ${1.1}
    Boolean              ${None}                   ${None}

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
    String               ${LIST}                   "[${u}'foo', ${u}'bar']"

Invalid string
    [Template]           Conversion Should Fail
    String               ${{type('Bang', (), {'__str__': lambda self: 1/0})()}}
    ...                  arg_type=Bang             error=ZeroDivisionError: *

Invalid string (non-ASCII byte string)
    [Tags]               require-py2
    [Template]           Conversion Should Fail
    String               ${{'åäö'}}                arg_type=string    error=*

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
    [Tags]               require-py3
    Bytestring           foo                       b'foo'
    Bytestring           \x00\x01\xFF\u00FF        b'\\x00\\x01\\xFF\\xFF'
    Bytestring           Hyvä esimerkki!           b'Hyv\\xE4 esimerkki!'
    Bytestring           None                      b'None'
    Bytestring           NONE                      b'NONE'
    Bytestring           ${{b'foo'}}               b'foo'
    Bytestring           ${{bytearray(b'foo')}}    b'foo'

Invalid bytesstring
    [Tags]               require-py3
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
    [Tags]               require-enum
    Enum                 FOO                       MyEnum.FOO
    Enum                 bar                       MyEnum.bar
    Enum                 foo                       MyEnum.foo

Normalized enum member match
    [Tags]               require-enum
    Enum                 b a r                     MyEnum.bar
    Enum                 BAr                       MyEnum.bar
    Enum                 B_A_r                     MyEnum.bar
    Enum                 normalize_me              MyEnum.normalize_me
    Enum                 normalize me              MyEnum.normalize_me
    Enum                 Normalize Me              MyEnum.normalize_me

Normalized enum member match with multiple matches
    [Tags]               require-enum
    [Template]           Conversion Should Fail
    Enum                 Foo                       type=MyEnum           error=MyEnum has multiple members matching 'Foo'. Available: 'FOO' and 'foo'

Invalid Enum
    [Tags]               require-enum
    [Template]           Conversion Should Fail
    Enum                 foobar                    type=MyEnum           error=MyEnum does not have member 'foobar'. Available: 'FOO', 'bar', 'foo' and 'normalize_me'
    Enum                 bar!                      type=MyEnum           error=MyEnum does not have member 'bar!'. Available: 'FOO', 'bar', 'foo' and 'normalize_me'

NoneType
    NoneType             None                      None
    NoneType             NONE                      None

Invalid NoneType
    [Template]           Conversion Should Fail
    NoneType             Hello, world!             type=None
    NoneType             True                      type=None
    NoneType             []                        type=None

None
    None                 None                      None
    None                 NONE                      None

Invalid None
    [Template]           Conversion Should Fail
    None                 Hello, world!             type=None
    None                 True                      type=None
    None                 []                        type=None

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
    Dictionary           True                                            error=Value is boolean, not dict.
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
    [Tags]               require-py3
    Set                  set()                     set()
    Set                  {'foo', 'bar'}            {'foo', 'bar'}
    Set                  {1, 2, 3.14, -42}         {1, 2, 3.14, -42}
    Set                  ${{{1}}}                  {1}
    Set                  ${{frozenset({1})}}       {1}
    Set                  ${{[1]}}                  {1}
    Set                  ${{(1,)}}                 {1}
    Set                  ${{{1: 2}}}               {1}

Invalid set
    [Tags]               require-py3
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
    [Tags]               require-py3
    Set abc              set()                     set()
    Set abc              {'foo', 'bar'}            {'foo', 'bar'}
    Set abc              {1, 2, 3.14, -42}         {1, 2, 3.14, -42}
    Mutable set          set()                     set()
    Mutable set          {'foo', 'bar'}            {'foo', 'bar'}
    Mutable set          {1, 2, 3.14, -42}         {1, 2, 3.14, -42}

Invalid set (abc)
    [Tags]               require-py3
    [Template]           Conversion Should Fail
    Set abc              {1, ooops}                type=set              error=Invalid expression.
    Set abc              {}                        type=set              error=Value is dictionary, not set.
    Set abc              ooops                     type=set              error=Invalid expression.
    Mutable set          {1, ooops}                type=set              error=Invalid expression.
    Mutable set          {}                        type=set              error=Value is dictionary, not set.
    Mutable set          ooops                     type=set              error=Invalid expression.

Frozenset
    [Tags]               require-py3
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
    [Tags]               require-py3
    [Template]           Conversion Should Fail
    Frozenset            {1, ooops}                                      error=Invalid expression.
    Frozenset            {}                                              error=Value is dictionary, not set.
    Frozenset            ooops                                           error=Invalid expression.
    Frozenset            {{'not', 'hashable'}}                           error=Evaluating expression failed: *

Sets are not supported in Python 2
    [Tags]               require-py2
    [Template]           Conversion Should Fail
    Set                  set()                                           error=Sets are not supported on Python 2.
    Set                  {'foo', 'bar'}                                  error=Sets are not supported on Python 2.
    Set abc              set()                     type=set              error=Sets are not supported on Python 2.
    Mutable set          {'foo', 'bar'}            type=set              error=Sets are not supported on Python 2.
    Frozenset            set()                                           error=Sets are not supported on Python 2.
    Frozenset            {'foo', 'bar'}                                  error=Sets are not supported on Python 2.
    Frozenset            frozenset()                                     error=Sets are not supported on Python 2.

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
    [Tags]               require-py3
    Kwonly               argument=1.0              expected=1.0
    Kwonly               argument=${1}             expected=1.0

Invalid kwonly
    [Tags]               require-py3
    [Template]           Conversion Should Fail
    Kwonly               argument=foobar           type=float
    Kwonly               argument=${NONE}          type=float    arg_type=None

Invalid type spec causes error
    [Documentation]    FAIL No keyword with name 'Invalid type spec' found.
    [Tags]    negative
    Invalid type spec

Non-matching argument name causes error
    [Documentation]    FAIL No keyword with name 'Non matching name' found.
    [Tags]    negative
    Non matching name

Type can be given to `return` without an error
    Return type          42                        42

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
    Type and default 1    BANG!    type=list         error=Invalid expression.
    Type and default 3    BANG!    type=timedelta    error=Invalid time string 'BANG!'.

Multiple types using Union
    [Tags]        require-py3
    [Template]    Multiple types using Union
    1             1
    1.2           1.2
    NONE          None
    ${1}          1
    ${1.2}        1.2
    ${None}       None

Argument not matching Union tupes
    [Tags]        require-py3
    [Template]    Conversion Should Fail
    Multiple types using Union    invalid    type=integer or None or float
    Multiple types using Union    ${LIST}    type=integer or None or float    arg_type=list

Multiple types using tuple
    [Template]    Multiple types using tuple
    1             1
    1.2           1.2
    NONE          None
    ${1}          1
    ${1.2}        1.2
    ${None}       None

Argument not matching tuple tupes
    [Template]    Conversion Should Fail
    Multiple types using tuple    invalid    type=integer or None or float
    Multiple types using tuple    ${LIST}    type=integer or None or float    arg_type=list
