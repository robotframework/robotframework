*** Settings ***
Library         ReturnTypes  # Lives in test/library_resources
Library         ArgumentTypes  # Lives in test/library_resources

*** Test Cases ***
String Arg
    argumenttypes.String  Hello world

Char Arg
    [Documentation]  FAIL TypeError: char1(): 1st arg can't be coerced to char
    Char 1  x
    Char 2  y
    Char 1  too many chars

Boolean Arg
    Boolean 1  ${True}
    Boolean 2  ${false}
    Boolean 2  true

Double Arg
    [Documentation]  FAIL ValueError: Argument at position 1 cannot be coerced to floating point number.
    Double 1  ${3.14}
    Double 2  ${10e2}
    Double 1  1nv4l1d

Float Arg
    [Documentation]  FAIL ValueError: Argument at position 1 cannot be coerced to floating point number.
    Float 1  ${-3.14}
    Float 2  ${-10e-2}
    Float 2  1nv4l1d

Long Arg
    [Documentation]  FAIL TypeError: long1(): 1st arg can't be coerced to long
    Long 1  ${1000000000000000}  # 15 x 0
    Long 2  ${-1}
    Long 1  ${1.1}

Integer Arg
    [Documentation]  FAIL TypeError: integer2(): 1st arg can't be coerced to java.lang.Integer
    Integer 1  ${42}
    Integer 2  ${-1}
    Integer 2  ${1000000000000000}

Short Arg
    [Documentation]  FAIL TypeError: short1(): 1st arg can't be coerced to short
    Short 1  ${2006}
    Short 2  ${-100}
    Short 1  ${1000000000000000}

Byte Arg
    [Documentation]  FAIL TypeError: byte1(): 1st arg can't be coerced to byte
    Byte 1  ${8}
    Byte 2  ${0}
    Byte 1  ${1000000000000000}

String Array Arg
    [Documentation]  FAIL TypeError: string_array(): 1st arg can't be coerced to String[]
    String Array  Hello  my  world
    String Array  Hi your tellus
    String Array
    ${list_args} =  Create List  Moi  maailma
    String Array  ${list_args}
    ${array_args} =  Return String Array
    String Array  ${array_args}
    ${int_array_args} =  Return Int Array
    String Array  ${int_array_args}

Integer Array Arg
    [Documentation]  FAIL TypeError: integer2_array(): 1st arg can't be coerced to java.lang.Integer[]
    Integer 1 Array  ${1}  ${2}  ${3}
    Integer 2 Array  ${-2006}  ${2006}
    Integer 1 Array
    Integer 2 Array
    ${list_args} =  Create List  ${-1}  ${1}
    Integer 1 Array  ${list_args}
    Integer 2 Array  ${list_args}
    ${int_array_args} =  Return Int Array
    Integer 1 Array  ${int_array_args}
    Integer 2 Array  ${int_array_args}  # fails because args is int[] and not java.lang.Integer[]

Return Integer
    [Documentation]  FAIL 2 (integer) != 2 (string)
    ${int} =  Return integer
    Should Be Equal  ${int}  ${2}
    Should Be Equal  ${int}  2

Return Double
    [Documentation]  FAIL 3.14 (float) != 3.14 (string)
    ${double} =  Return double
    Should Be Equal  ${double}  ${3.14}
    Should Be Equal  ${double}  3.14

Return Boolean
    ${boolean} =  Return Boolean
    Should Be True  ${boolean}
    ${boolean} =  Convert To Boolean  ${boolean}
    Should Be True  ${boolean}

Return String
    ${string} =  Return String
    Should Be Equal  ${string}  Hello world

Return Null
    ${mynull} =  Return Null
    Should Be Equal  ${mynull}  ${null}

Return String Array
    ${string array} =  Return String Array
    Check String Array  ${string array}

Return Int Array
    ${int array} =  Return Int Array
    Check Int Array  ${int array}
