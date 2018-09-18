*** Settings ***
Library           ArgumentsJava    Arg    and    varargs    accepted
Library           ListArgumentsJava    Arg    and    varargs    accepted
Library           ArgumentTypes
Library           ExampleJavaLibrary
Library           Collections

*** Variables ***
@{LIST}           With    three    values

*** Test Cases ***
Correct Number Of Arguments When No Defaults Or Varargs
    ${ret} =    A 0
    Should Be Equal    ${ret}    a_0
    ${ret} =    A 1    my arg
    Should Be Equal    ${ret}    a_1: my arg
    ${ret} =    A 3    a1    a2    a3
    Should Be Equal    ${ret}    a_3: a1 a2 a3

Too Few Arguments When No Defaults Or Varargs 1
    [Documentation]    FAIL Keyword 'ArgumentsJava.A 1' expected 1 argument, got 0.
    A 1

Too Few Arguments When No Defaults Or Varargs 2
    [Documentation]    FAIL Keyword 'ArgumentsJava.A 3' expected 3 arguments, got 2.
    A 3    a1    a2

Too Many Arguments When No Defaults Or Varargs 1
    [Documentation]    FAIL Keyword 'ArgumentsJava.A 0' expected 0 arguments, got 10.
    A 0    This    is    too    much    !    Really
    ...    way    too    much    !!!!!

Too Many Arguments When No Defaults Or Varargs 2
    [Documentation]    FAIL Keyword 'ArgumentsJava.A 1' expected 1 argument, got 2.
    A 1    Too    much

Too Many Arguments When No Defaults Or Varargs 3
    [Documentation]    FAIL Keyword 'ArgumentsJava.A 3' expected 3 arguments, got 4.
    A 3    a1    a2    a3    a4

Correct Number Of Arguments With Defaults
    ${ret} =    A 0 1
    Should Be Equal    ${ret}    a_0_1: default
    ${ret} =    A 0 1    This works too
    Should Be Equal    ${ret}    a_0_1: This works too
    ${ret} =    A 1 3    My argument
    Should Be Equal    ${ret}    a_1_3: My argument default default
    ${ret} =    A 1 3    My argument    My argument 2
    Should Be Equal    ${ret}    a_1_3: My argument My argument 2 default
    ${ret} =    A 1 3    My argument    My argument 2    My argument 3
    Should Be Equal    ${ret}    a_1_3: My argument My argument 2 My argument 3

Java Varargs Should Work
    ${ret} =    Java Varargs    My Argument 1    My Argument 2
    Should Be Equal    ${ret}    javaVarArgs: My Argument 1 My Argument 2
    ${ret} =    Java Varargs
    Should Be Equal    ${ret}    javaVarArgs:

Too Few Arguments With Defaults
    [Documentation]    FAIL Keyword 'ArgumentsJava.A 1 3' expected 1 to 3 arguments, got 0.
    A 1 3

Too Many Arguments With Defaults 1
    [Documentation]    FAIL Keyword 'ArgumentsJava.A 0 1' expected 0 to 1 arguments, got 2.
    A 0 1    Too    much

Too Many Arguments With Defaults 2
    [Documentation]    FAIL Keyword 'ArgumentsJava.A 1 3' expected 1 to 3 arguments, got 4.
    A 1 3    This    is    too    much

Correct Number Of Arguments With Varargs
    [Template]    Verify varargs for array and list
    a_0
    a_0       My arg
    a_0       1    2    3    4
    a_1       Required arg
    a_1       Required arg    plus one
    a_1       1 (req)    2    3    4    5    6    7    8    9

Too Few Arguments With Varargs
    [Documentation]    FAIL Keyword 'ArgumentsJava.A 1 N' expected at least 1 argument, got 0.
    A 1 N

Too Few Arguments With Varargs List
    [Documentation]    FAIL Keyword 'ListArgumentsJava.A 1 List' expected at least 1 argument, got 0.
    A 1 List

Varargs Work Also With Arrays
    ${list} =    Create List    Hello    string    array    world
    ${array1} =    Get String Array    ${list}
    ${array2} =    Get String Array    ${array1}
    ${array3} =    Get String Array    Hello    string    array    world
    Should Be Equal    ${array1}    ${array2}
    Should Be Equal    ${array2}    ${array3}

Varargs Work Also With Lists
    ${list} =      Create List    Hello    string    array    world
    ${array1} =    Get String Array    ${list}
    @{list1} =     Get String Array    ${list}
    ${list2} =     Get String List    ${list}
    String List    ${list}
    String List    ${list1}
    String List    ${list2}
    String List    @{array1}
    String List    ${array1.tolist()}
    String List    Hello    string    list    world

Kwargs
   ${res} =       javaKWArgs    foo=one   bar=two
   Should be equal    ${res}    javaKWArgs: bar:two foo:one

Normal and Kwargs
   ${res} =       javaNormalAndKWArgs    hello   foo=one   bar=two
   Should be equal    ${res}    javaNormalAndKWArgs: hello bar:two foo:one

Varargs and Kwargs
   ${res} =       javaVarArgsAndKWArgs    hello   kitty  foo=one   bar=two
   Should be equal    ${res}    javaVarArgsAndKWArgs: hello kitty bar:two foo:one

All args
   ${res} =       javaAllArgs    arg   hello   kitty  foo=one   bar=two
   Should be equal    ${res}    javaAllArgs: arg hello kitty bar:two foo:one

Too many positional with kwargs 1
    [Documentation]     FAIL Keyword 'ArgumentsJava.Java KW Args' expected 0 non-named arguments, got 3.
    Java kwargs    too    many    positional    foo=bar

Too many positional with kwargs 2
    [Documentation]     FAIL Keyword 'ArgumentsJava.Java Normal And KW Args' expected 1 non-named argument, got 3.
    Java normal and kwargs    too    many    positional    foo=bar

Java kwargs wont be interpreted as values for positional arguments
   ${res} =       javaManyNormalArgs    foo   huu   arg1=one
   Should be equal    ${res}    javaManyNormalArgs: foo huu arg1:one

Map can be given as an argument still
   ${map} =       getJavaMap    foo=one   bar=two
   ${res} =       javaKWArgs    ${map}
   Should be equal    ${res}    javaKWArgs: bar:two foo:one

Dict can be given as an argument still
   ${dict} =      Create dictionary     foo=one   bar=two
   ${res} =       javaKWArgs    ${dict}
   Should be equal    ${res}    javaKWArgs: bar:two foo:one

Hashmap is not kwargs
    [Documentation]    FAIL Keyword 'ArgumentsJava.Hashmap Arg' expected 1 argument, got 2.
    ${map} =       getJavaMap    foo=one   bar=two
    ${res} =       hashmapArg    ${map}
    Should be equal    ${res}    hashmapArg: bar:two foo:one
    hashmapArg    foo=bar   doo=daa

Valid Arguments For Keyword Expecting Non String Scalar Arguments
    Byte 1    ${1}
    Byte 2    ${2}
    Short 1    ${100}
    Short 2    ${-200}
    Integer 1    ${100000}
    Integer 2    ${-200000}
    Long 1    ${1000000000000}
    Long 2    ${-2000000000000}
    Float 1    ${3.14}
    Float 2    ${0}
    Double 1    ${10e10}
    Double 2    ${-10e-10}
    Boolean 1    ${True}
    Boolean 2    ${False}
    Char 1    x
    Char 2    y
    Object    Hello
    Object    ${42}
    Object    ${3.14}
    Object    ${true}
    Object    ${null}
    ${obj} =    Get Java Object    my name
    Object    ${obj}
    ${ht} =    Get Hashtable
    Object    ${ht}
    Set To Hashtable    ${ht}    my key    my value
    Check In Hashtable    ${ht}    my key    my value

Valid Arguments For Keyword Expecting Non String Array Arguments
    Byte 1 Array
    Byte 1 Array    ${0}    ${1}    ${2}
    Byte 2 Array
    Byte 2 Array    ${0}    ${1}    ${2}
    Short 1 Array
    Short 1 Array    ${0}    ${1}    ${2}
    Short 2 Array
    Short 2 Array    ${0}    ${1}    ${2}
    Integer 1 Array
    Integer 1 Array    ${0}    ${1}    ${2}    ${10000}    ${-10000}
    Integer 2 Array
    Integer 2 Array    ${0}    ${1}    ${2}    ${10000}    ${-10000}
    Long 1 Array
    Long 1 Array    ${0}    ${1}    ${2}    ${10000}    ${-10000}
    Long 2 Array
    Long 2 Array    ${0}    ${1}    ${2}    ${10000}    ${-10000}
    Float 1 Array
    Float 1 Array    ${0}    ${1}    ${2}    ${-3.14}    ${10*3}
    Float 2 Array
    Float 2 Array    ${0}    ${1}    ${2}    ${-3.14}    ${10*3}
    Double 1 Array
    Double 1 Array    ${0}    ${1}    ${2}    ${-3.14}    ${10*3}
    Double 2 Array
    Double 2 Array    ${0}    ${1}    ${2}    ${-3.14}    ${10*3}
    Boolean 1 Array
    Boolean 1 Array    ${True}    ${False}    ${True}    ${False}
    Boolean 2 Array
    Boolean 2 Array    ${True}    ${False}    ${True}    ${False}
    Char 1 Array
    Char 1 Array    c    h    a    r    s
    Char 2 Array
    Char 2 Array    c    h    a    r    s
    ${obj} =    Get Java Object    my name
    ${ht} =    Get Hashtable
    Object Array
    Object Array    ${obj}    ${ht}    hello world    ${42}    ${null}

Valid Arguments For Keyword Expecting Non String List Arguments
    Integer List
    Integer List    ${0}    ${1}    ${2}    ${10000}    ${-10000}
    Double List
    Double List    ${0.}    ${1.}    ${2.}    ${-3.14}    ${10*3.}
    Boolean List
    Boolean List    ${True}    ${False}    ${True}    ${False}
    ${obj} =    Get Java Object    my name
    ${ht} =    Get Hashtable
    Object List
    Object List    ${obj}    ${ht}    hello world    ${42}    ${null}

Invalid Argument Types 1
    [Documentation]    FAIL ValueError: Argument at position 1 cannot be coerced to integer.
    Integer 1    this is not an integer

Invalid Argument Types 2
    [Documentation]    FAIL TypeError: short1(): 1st arg can't be coerced to short
    Short 1    ${10000000000000000}

Invalid Argument Types 3
    [Documentation]    FAIL TypeError: char2(): 1st arg can't be coerced to java.lang.Character
    Char 2    this is a string and not a char

Invalid Argument Types 4
    [Documentation]    FAIL TypeError: checkInHashtable(): 1st arg can't be coerced to java.util.Hashtable
    Check In Hashtable    string, not a hashtable    key    value

Invalid Argument Types 5
    [Documentation]    FAIL TypeError: integer2_array(): 1st arg can't be coerced to java.lang.Integer[]
    Integer 2 Array    ${1}    ${2}    3

Invalid Argument Types 6
    [Documentation]    FAIL TypeError: string_array(): 1st arg can't be coerced to String[]
    String Array    1    2    ${3}

Invalid Argument Types 7
    [Documentation]    FAIL TypeError: string(): 1st arg can't be coerced to String
    ArgumentTypes.String    ${42}

Calling Using List Variables
    A 0    @{EMPTY}
    A 1    @{EMPTY}    arg
    A 3    @{LIST}
    A 3    @{LIST}    @{EMPTY}

*** Keywords ***
Verify varargs for array and list
    [Arguments]    ${keyword}   @{args}
    Verify varargs   ${keyword}_n      @{args}
    Verify varargs   ${keyword}_list   @{args}

Verify varargs
    [Arguments]    ${keyword}   @{args}
    ${expected} =    Catenate    ${keyword}:    @{args}
    ${res}=    Run keyword    ${keyword}     @{args}
    Should be equal    ${res}    ${expected}
