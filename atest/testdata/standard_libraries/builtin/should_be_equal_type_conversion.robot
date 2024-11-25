*** Settings ***
Test Template     Should Be Equal

*** Test Cases ***
Convert second argument using `type`
    ${42}               42               type=int
    42                  ${42}            type=${{str}}
    ${False}            no               type=Boolean
    ${{[1, 2, 'x']}}    [1, 2.0, 'x']    type=list[int|str]
    Cat                 cat              type=Literal["Dog", "Cat", "Cow"]

Automatic `type`
    ${42}               42               type=auto
    42                  ${42}            type=AUTO
    ${False}            no               type=Auto
    ${{[1, 2, 3]}}      [1, 2, 3]        type=AuTo

Automatic `type` doesn't handle nested types
    [Documentation]    FAIL    [1, 2, 3] != [1, 2, '3']
    ${{[1, 2, 3]}}      [1, 2, '3']      type=auto

First argument must match `type`
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) ValueError: Argument 'first' got value '42' that does not match type 'int'.
    ...
    ...    2) ValueError: Argument 'first' got value [1, 2] that does not match type 'list[str]'.
    42                   42              type=int
    ${{[1, 2]}}          ['1', '2']      type=list[str]

Conversion fails with `type`
    [Documentation]    FAIL    ValueError: Argument 'second' got value 'bad' that cannot be converted to integer.
    ${42}               bad              type=int

Invalid type with `type`
    [Documentation]    FAIL    TypeError: Cannot convert type 'bad'.
    ${42}               whatever         type=bad

Convert both arguments using `types`
    ${42}               42               types=int
    42                  ${42}            types=${{str}}
    ${False}            no               types=Boolean
    ${{[1, 2, 'x']}}    [1, 2.0, 'x']    types=list[int|str]
    42                  42               types=int
    ${{[1, 2]}}         ['1', '2']       types=list[str]

Conversion fails with `types`
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) ValueError: Argument 'first' got value 'bad' that cannot be converted to integer.
    ...
    ...    2) ValueError: Argument 'second' got value 'bad' that cannot be converted to decimal.
    bad                 2                types=int
    1                   bad              types=decimal

Invalid type with `types`
    [Documentation]    FAIL    TypeError: Cannot convert type 'oooops'.
    ${42}               whatever         types=oooops

Cannot use both `type` and `types`
    [Documentation]    FAIL    TypeError: Cannot use both 'type' and 'types' arguments.
    1                   1                type=int    types=int

Automatic type doesn't work with `types`
    [Documentation]    FAIL    TypeError: Cannot convert type 'auto'.
    ${42}               ${42}            types=auto
