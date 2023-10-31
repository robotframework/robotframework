*** Variables ***
&{DICT}          a=1    b=2    c=3
@{result}

*** Test Cases ***
FOR loop with one variable
    FOR    ${item}    IN    &{DICT}
        Should be true    isinstance($item, tuple)
        Length should be    ${item}    2
        @{result} =    Create list    @{result}    ${item}[0]:${item}[1]
    END
    Should be true    ${result} == ['a:1', 'b:2', 'c:3']

FOR loop with two variables
    FOR    ${key}    ${value}    IN    &{DICT}
        @{result} =    Create list    @{result}    ${key}:${value}
    END
    Should be true    ${result} == ['a:1', 'b:2', 'c:3']

FOR loop with more than two variables is invalid
    [Documentation]    FAIL
    ...    Number of FOR loop variables must be 1 or 2 when iterating over dictionaries, got 3.
    FOR    ${too}    ${many}    ${variables}    IN    &{DICT}
        Fail    Not executed
    END
    Fail    Not executed

FOR IN ENUMERATE loop with one variable
    FOR    ${var}    IN ENUMERATE    &{DICT}
        Should be true    isinstance($var, tuple)
        Length should be    ${var}    3
        @{result} =    Create list    @{result}    ${var}[0]:${var}[1]:${var}[2]
    END
    Should be true    ${result} == ['0:a:1', '1:b:2', '2:c:3']

FOR IN ENUMERATE loop with two variables
    FOR    ${index}    ${item}    IN ENUMERATE   &{DICT}
        Should be true    isinstance($index, int)
        Should be true    isinstance($item, tuple)
        Length should be    ${item}    2
        @{result} =    Create list    @{result}    ${index}:${item}[0]:${item}[1]
    END
    Should be true    ${result} == ['0:a:1', '1:b:2', '2:c:3']

FOR IN ENUMERATE loop with three variables
    FOR    ${i}    ${k}    ${v}    IN ENUMERATE   &{DICT}
        Should be true      isinstance($i, int)
        @{result} =    Create list    @{result}    ${i}:${k}:${v}
    END
    Should be true    ${result} == ['0:a:1', '1:b:2', '2:c:3']

FOR IN ENUMERATE loop with start
    FOR    ${i}    ${k}    ${v}    IN ENUMERATE   &{DICT}    start=42
        Should be true      isinstance($i, int)
        @{result} =    Create list    @{result}    ${i}:${k}:${v}
    END
    Should be true    ${result} == ['42:a:1', '43:b:2', '44:c:3']

FOR IN ENUMERATE loop with more than three variables is invalid
    [Documentation]    FAIL
    ...    Number of FOR IN ENUMERATE loop variables must be 1-3 when iterating over dictionaries, got 4.
    FOR    ${too}    ${many}    ${variables}    ${here}    IN ENUMERATE    &{DICT}
        Fail    Not executed
    END
    Fail    Not executed

FOR IN RANGE loop doesn't support dict iteration
    [Documentation]    FAIL
    ...    FOR IN RANGE loops do not support iterating over dictionaries.
    FOR    ${x}    IN RANGE    &{DICT}
        Fail    Not executed
    END
    Fail    Not executed

FOR IN ZIP loop doesn't support dict iteration
    [Documentation]    FAIL
    ...    FOR IN ZIP loops do not support iterating over dictionaries.
    FOR    ${x}    IN ZIP   &{DICT}
        Fail    Not executed
    END
    Fail    Not executed

Multiple dict variables
    &{d} =    Create dictionary    d=4
    FOR    ${key}    ${value}    IN    &{DICT}    &{d}    &{{{'e': 5}}}    &{EMPTY}
        @{result} =    Create list    @{result}    ${key}:${value}
    END
    Should be true    ${result} == ['a:1', 'b:2', 'c:3', 'd:4', 'e:5']

Dict variable with 'key=value' syntax
    FOR    ${key}    ${value}    IN    =0    &{DICT}    d=${4}    ${{'e'}}=
    ...    f\==3    \=\====
        @{result} =    Create list    @{result}    ${key}:${value}
    END
    Should be true    ${result} == [':0', 'a:1', 'b:2', 'c:3', 'd:4', 'e:', 'f=:3', '==:==']

Last value wins
    FOR    ${key}    ${value}    IN    =over    a=ridded    &{DICT}    c=replace
    ...    &{EMPTY}    ====    &{{{'d': 'new', 'b': 'override'}}}    =
        @{result} =    Create list    @{result}    ${key}:${value}
    END
    Should be true    ${result} == [':', 'a:1', 'b:override', 'c:replace', 'd:new']

Equal sign in variable
    FOR    ${key}    ${value}    IN    a=${{'='}}    ${{'='}}=b    ${{'=='}}=
    ...    &{{{'===': ''}}}
        @{result} =    Create list    @{result}    ${key}:${value}
    END
    Should be true    ${result} == ['a:=', '=:b', '==:', '===:']

'key=value' alone is still considered "normal" iteration
    FOR    ${item}    IN    a=1    b=2
        @{result} =    Create list    @{result}    ${item.upper()}
    END
    Should be true    ${result} == ['A=1', 'B=2']
    FOR    ${x}    ${y}    IN    x==1    y==2
        Should be equal    ${x}    x==1
        Should be equal    ${y}    y==2
    END

Non-string keys
    FOR    ${key}    ${value}    IN    ${1}=one    &{{{2: 'two'}}}
        Should be true    isinstance($key, int)
        @{result} =    Create list    @{result}    ${key}:${value}
    END
    Should be true    ${result} == ['1:one', '2:two']

Invalid key
    [Documentation]    FAIL
    ...    STARTS: Invalid dictionary item '\${{[]}}=ooops': TypeError:
    FOR    ${x}    IN    ${{[]}}=ooops    &{EMPTY}
        Fail    Not executed
    END
    Fail    Not executed

Invalid dict 1
    [Documentation]    FAIL
    ...    Value of variable '\&{TEST NAME}' is not dictionary or dictionary-like.
    FOR    ${x}    IN    &{TEST NAME}
        Fail    Not executed
    END
    Fail    Not executed

Invalid dict 2
    [Documentation]    FAIL
    ...    STARTS: Resolving variable '\&{{{[]: 'ooops'}}}' failed: \
    ...    Evaluating expression "{[]: 'ooops'}" failed: TypeError:
    FOR    ${x}    IN    &{{{[]: 'ooops'}}}
        Fail    Not executed
    END
    Fail    Not executed

Non-existing variable 1
    [Documentation]    FAIL Variable '\&{NON EXISTING}' not found.
    FOR    ${x}    IN    &{NON EXISTING}
        Fail    Not executed
    END
    Fail    Not executed

Non-existing variable 2
    [Documentation]    FAIL Variable '\${non existing}' not found.
    FOR    ${x}    IN    &{EMPTY}    key=${non existing}
        Fail    Not executed
    END
    Fail    Not executed

Dict variables and invalid values 1
    [Documentation]    FAIL
    ...    Invalid FOR loop value 'ååps'. When iterating over dictionaries, \
    ...    values must be '\&{dict}' variables or use 'key=value' syntax.
    FOR    ${x}    IN    &{DICT}    ååps    b=x
        Fail    Not executed
    END
    Fail    Not executed

Dict variables and invalid values 2
    [Documentation]    FAIL
    ...    Invalid FOR loop value '\${{'='}}'. When iterating over dictionaries, \
    ...    values must be '\&{dict}' variables or use 'key=value' syntax.
    FOR    ${i}    IN    &{DICT}    ${{'='}}
        Fail    Not executed
    END
    Fail    Not executed

Dict variables and invalid values 3
    [Documentation]    FAIL
    ...    Invalid FOR loop value 'invalid'. When iterating over dictionaries, \
    ...    values must be '\&{dict}' variables or use 'key=value' syntax.
    FOR    ${i}    IN    invalid    &{DICT}
        Fail    Not executed
    END
    Fail    Not executed

Equal sign in variable doesn't initiate dict iteration
    FOR    ${item}    IN    ${{'='}}    @{{['=']}}
        Should be equal    ${item}    =
    END

'key=value' syntax with normal values doesn't initiate dict iteration 1
    FOR    ${item}    IN    a=1    normal    c=3
        Should be true    isinstance($item, type(u'string'))
        @{result} =    Create list    @{result}    ${item}
    END
    Should be true    ${result} == ['a=1', 'normal', 'c=3']

'key=value' syntax with normal values doesn't initiate dict iteration 2
    FOR    ${item}    IN    a=1    b\=2    c=3
        Should be true    isinstance($item, type(u'string'))
        @{result} =    Create list    @{result}    ${item}
    END
    Should be true    ${result} == ['a=1', 'b=2', 'c=3']
