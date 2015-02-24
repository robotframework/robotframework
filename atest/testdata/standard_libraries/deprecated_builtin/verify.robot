*** Variable ***
${str0}           0
${str1}           1
${int0}           ${0}
${int1}           ${1}

*** Test Case ***
Error
    [Documentation]    FAIL Exception
    Error

Error With Message
    [Documentation]    FAIL Error message
    Error    Error message

Fail If 1
    [Documentation]    FAIL '0 < 1' should not be true.
    Fail If    0 > 1
    Is False    ${int0} < ${int1}

Fail If 2
    [Documentation]    FAIL My message
    Fail If    True    My message

Fail Unless 1
    [Documentation]    FAIL '1 != 1 and True or False' should be true.
    Fail Unless    -1 <= ${str1} <= 1
    Is True    -${str1} < ${str0} < ${str1}
    Fail Unless    1 != 1 and True or False

Fail Unless 2
    [Documentation]    FAIL My error message
    Fail Unless    False    My error message

Fail If Equal
    [Documentation]    FAIL 1 == 1
    Fail If Equal    ${str1}    Not ${str1}
    Not Equal    ${str1}    1

Fail Unless Equal
    [Documentation]    FAIL Error message: 1 (string) != 1 (number)
    Fail Unless Equal    ${str1}    1
    Equals    ${str1}    ${int1}    Error message

Fail If Ints Equal
    [Documentation]    FAIL This message only
    Fail If Ints Equal    1    ${str0}
    Ints not Equal    0    ${int1}
    Fail If Ints Equal    1    ${int1}    This message only    No values

Fail Unless Ints Equal
    [Documentation]    FAIL -1 != 1
    Fail Unless Ints Equal    ${str1}${str0}${str0}    ${str1}${str0}${str0}
    Ints Equal    -${str1}    ${str1}

Fail If Floats Equal
    [Documentation]    FAIL Fails again: 1.1 == 1.1
    Fail If Floats Equal    ${str1}.${str1}    1.2
    Floats Not Equal    ${str1}.${str1}    1.1    Fails again

Fail Unless Floats Equal
    [Documentation]    FAIL Only this message again
    Fail Unless Floats Equal    ${str1}    ${str1}.${str0}${str0}
    Floats Equal    ${str1}.000001    ${str1}.${str0}${str0}${str1}    Only this message again    False

Fail If Starts
    [Documentation]    FAIL 'Hello, world!' starts with 'Hello'
    Fail If Starts    Hello, world!    Hi
    Does not start    Hello, world!    Hello

Fail Unless Starts
    [Documentation]    FAIL My message: 'This is a big longer sentence and it even has a friend here. This is the friend of the previous sentence -- also this is quite long, actually even longer than its friend.' does not start with 'Whatever'
    Fail Unless Starts    ${str0}${str0}7    00
    Starts    This is a big longer sentence and it even has a friend here. This is the friend of the previous sentence -- also this is quite long, actually even longer than its friend.    Whatever    My message

Fail If Ends
    [Documentation]    FAIL Message only
    Fail If Ends    Hello!    Hello
    Does not end    Hillo!    !    Message only    No Values

Fail Unless Ends
    [Documentation]    FAIL '007' does not end with '00'
    Fail Unless Ends    ${str0}${str0}7    007
    Ends    ${str0}${str0}7    00

Fail If Contains
    [Documentation]    FAIL 'Hello yet again' contains 'yet'
    Fail If Contains    Hello again    yet
    Does not contain    Hello yet again    yet

Fail Unless Contains
    [Documentation]    FAIL Message: 'abcdefg' does not contain 'ABCDEFG'
    Fail Unless Contains    abcdefg    cd    Massage
    Contains    abcdefg    ABCDEFG    Message

Fail If Matches
    [Documentation]    FAIL 'Hello world' matches '?ello*'
    Fail If Matches    this string does not    match this pattern
    Fail If Matches    Case matters    case matters
    Does not match    Hello world    ?ello*

Fail Unless Matches
    [Documentation]    FAIL Failure: 'NOK' does not match 'OK'
    Fail Unless Matches    abcdefghijklmnopqrstuvwxyz    *?efg*p*t?vw*z
    Matches    NOK    OK    Failure

Fail If Regexp Matches
    [Documentation]    FAIL 'James Bond 007' matches '^J\\w{4}\\sB[donkey]+ \\d*$'
    Fail If Regexp Matches    this string does not    match this pattern
    Does not match regexp    James Bond ${str0}${str0}7    ^J\\w{4}\\sB[donkey]+ \\d*$

Fail Unless Regexp Matches
    [Documentation]    FAIL Something failed
    Fail Unless Regexp Matches    This is a multiline\nstring    (?im)^STR
    Matches regexp    \    OK    Something failed    No values
