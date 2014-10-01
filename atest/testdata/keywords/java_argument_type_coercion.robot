*** Settings ***
Documentation     These test check that types of arguments to keywords implemented in Java are coerced correctly. If the coercion is not correctly, a test would fail with message like TypeError: intArgument(): 1st arg can't be coerced to int
Library           ArgTypeCoercion    42    true

*** Test Cases ***
Coercing Integer Arguments
    [Documentation]    FAIL ValueError: Argument at position 1 cannot be coerced to integer.
    Int Argument    4
    Int Argument    0
    Int Argument    -42
    Int Argument    invalid

Coercing Boolean Arguments
    [Documentation]    FAIL ValueError: Argument at position 1 cannot be coerced to boolean.
    Boolean Argument    true
    Boolean Argument    FALSE
    Boolean Argument    invalid

Coercing Real Number Arguments
    [Documentation]    FAIL ValueError: Argument at position 1 cannot be coerced to floating point number.
    Double Argument    4.21
    Float Argument    -14444.876856
    Double Argument    0
    Float Argument    1.5e10
    Double Argument    invalid

Coercing Multiple Arguments
    ${ret} =    Coercable Keyword    0
    Should Be Equal    ${ret}    Got: 0.0 and 0 and false
    ${ret} =    Coercable Keyword    -1.0    42
    Should Be Equal    ${ret}    Got: -1.0 and 42 and false
    ${ret} =    Coercable Keyword    42.24    42    True
    Should Be Equal    ${ret}    Got: 42.24 and 42 and true

Coercing Fails With Conflicting Signatures
    [Documentation]    FAIL STARTS: TypeError: unCoercableKeyword(): 1st arg can't be coerced to
    Uncoercable Keyword    2    False

It Is Possible To Coerce Only Some Arguments
    Coercable And Uncoercable Args    Hello    True    24    9999
    Primitive and Array    5    ${43}    ${75}
