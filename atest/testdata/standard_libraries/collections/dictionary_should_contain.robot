*** Settings ***
Library           Collections
Library           CollectionsHelperLibrary.py

*** Variables ***
@{LIST}          a    B
${TUPLE}         ${{'a', 'B'}}
&{D}             a=x    B=Y    c=${3}   ${4}=E    ß=Straße    list=${LIST}    ${TUPLE}=tuple

*** Test Cases ***
### Should (Not) Contain Key ###

Should contain key
    [Documentation]    FAIL    Dictionary does not contain key 'bad'.
    [Template]         Dictionary Should Contain Key
    ${D}    a
    ${D}    ${4}
    ${D}    ß
    ${D}    ${TUPLE}
    ${D}    bad

Should contain key with custom message
    [Documentation]    FAIL    The message.
    [Template]         Dictionary Should Contain Key
    ${D}    a                  msg=Succeeds. Message not used.
    ${D}    bad                msg=The message.

Should contain key with `ignore_case`
    [Documentation]    FAIL    This fails.
    [Template]         Dictionary Should Contain Key
    ${D}    a                  ignore_case=True
    ${D}    A                  ignore_case=${True}
    ${D}    b                  ignore_case=key
    ${D}    B                  ignore_case=keys
    ${D}    ss                 ignore_case=casefold!
    ${D}    ${4}               ignore_case=non-string
    ${D}    ${{('A', 'b')}}    ignore_case=nested normalization
    ${D}    b                  ignore_case=value    msg=This fails.

Should not contain key
    [Documentation]    FAIL    Dictionary contains key 'c'.
    [Template]         Dictionary Should Not Contain Key
    ${D}    x
    ${D}    ${3}
    ${D}    ss
    ${D}    c

Should not contain key with custom message
    [Documentation]    FAIL    The message.
    [Template]         Dictionary Should Not Contain Key
    ${D}    xxx                msg=Succeeds. Message not used.
    ${D}    c                  msg=The message.

Should not contain key with `ignore_case`
    [Documentation]    FAIL    Dictionary contains key 'A'.
    [Template]         Dictionary Should Not Contain Key
    ${D}    d                  ignore_case=True
    ${D}    b                  ignore_case=values
    ${D}    A                  ignore_case=keys

### Should (Not) Contain Value ###

Should contain value
    [Documentation]    FAIL    Dictionary does not contain value '666'.
    [Template]         Dictionary Should Contain Value
    ${D}    x
    ${D}    ${3}
    ${D}    ${LIST}
    ${D}    ${666}

Should contain value with custom message
    [Documentation]    FAIL    The message.
    [Template]         Dictionary Should Contain Value
    ${D}    x                  msg=Succeeds. Message not used.
    ${D}    bad                msg=The message.

Should contain value with `ignore_case`
    [Documentation]    FAIL    This fails.
    [Template]         Dictionary Should Contain Value
    ${D}    x                  ignore_case=True
    ${D}    X                  ignore_case=True
    ${D}    y                  ignore_case=True
    ${D}    Y                  ignore_case=True
    ${D}    strasse            ignore_case=True
    ${D}    ${3}               ignore_case=value
    ${D}    ${{['A', 'b']}}    ignore_case=value
    ${D}    ${{['A', 'b']}}    ignore_case=key    msg=This fails.

Should not contain value
    [Documentation]    FAIL    Dictionary contains value '3'.
    [Template]         Dictionary Should Not Contain Value
    ${D}    a
    ${D}    ${TUPLE}
    ${D}    ${3}

Should not contain value with custom message
    [Documentation]    FAIL    The message.
    [Template]         Dictionary Should Not Contain Value
    ${D}    a                  msg=Succeeds. Message not used.
    ${D}    ${3}               msg=The message.

Should not contain value with `ignore_case`
    [Documentation]    FAIL    This fails.
    [Template]         Dictionary Should Not Contain Value
    ${D}    a    ignore_case=True
    ${D}    e    ignore_case=key
    ${D}    X    ignore_case=key
    ${D}    e    ignore_case=value    msg=This fails.

### Should Contain Item ###

Should contain item
    [Template]    Dictionary Should Contain Item
    ${D}    a           x
    ${D}    c           ${3}
    ${D}    ${4}        E
    ${D}    ß           Straße
    ${D}    ${TUPLE}    tuple
    ${D}    list        ${LIST}

Should contain item with missing key
    [Documentation]    FAIL     Dictionary does not contain key 'bad'.
    Dictionary Should Contain Item    ${D}    bad    whatever

Should contain item with missing key and custom message
    [Documentation]    FAIL     The message.
    Dictionary Should Contain Item    ${D}    bad    whatever    msg=The message.

Should contain item with wrong value
    [Documentation]    FAIL     Value of dictionary key 'a' does not match: x != bad
    Dictionary Should Contain Item    ${D}    a    bad

Should contain item with wrong value and custom message
    [Documentation]    FAIL    The message.
    Dictionary Should Contain Item    ${D}    a    bad    msg=The message.

Should contain item with values looking same but having different types
    [Documentation]    FAIL Value of dictionary key 'c' does not match: 3 (integer) != 3 (string)
    Dictionary Should Contain Item    ${D}    c    3

Should contain item with `ignore_case`
    [Documentation]    FAIL     Value of dictionary key 'A' does not match: x != bad
    [Template]         Dictionary Should Contain Item
    ${D}      a       x          ignore_case=True
    ${D}      a       X          ignore_case=${True}
    ${D}      A       x          ignore_case=both
    ${D}      A       X          ignore_case=xxx
    ${D}      b       y          ignore_case=True
    ${D}      b       Y          ignore_case=${True}
    ${D}      B       Y          ignore_case=both
    ${D}      B       Y          ignore_case=xxx
    ${D}      c       ${3}       ignore_case=true
    ${D}      C       ${3}       ignore_case=true
    ${D}      ${4}    e          ignore_case=true
    ${D}      ${4}    E          ignore_case=true
    ${D}      ß       Straße     ignore_case=true
    ${D}      ss      strasse    ignore_case=true
    ${D}      SS      STRASSE    ignore_case=true
    ${D}      LIST    ${{['A', 'b']}}
    ...                          ignore_case=true
    ${D}      ${{('A', 'b')}}
    ...               TUPLE      ignore_case=true
    ${D}      A       BAD        ignore_case=true

Should contain item with `ignore_case=key`
    [Documentation]    FAIL    Value of dictionary key 'ß' does not match: Straße != Strasse
    [Template]         Dictionary Should Contain Item
    ${D}      a       x          ignore_case=key
    ${D}      A       x          ignore_case=KEY
    ${D}      b       Y          ignore_case=Key
    ${D}      B       Y          ignore_case=keys
    ${D}      c       ${3}       ignore_case=KEYS
    ${D}      C       ${3}       ignore_case=Keys
    ${D}      ${4}    E          ignore_case=key
    ${D}      ß       Straße     ignore_case=key
    ${D}      ss      Straße     ignore_case=key
    ${D}      SS      Straße     ignore_case=key
    ${D}      ${{('A', 'b')}}
    ...               tuple      ignore_case=key
    ${D}      ß       Strasse    ignore_case=key

Should contain item with `ignore_case=value`
    [Documentation]    FAIL Dictionary does not contain key 'ss'.
    [Template]         Dictionary Should Contain Item
    ${D}      a       x          ignore_case=value
    ${D}      a       X          ignore_case=VALUE
    ${D}      B       y          ignore_case=Value
    ${D}      B       Y          ignore_case=values
    ${D}      c       ${3}       ignore_case=VALUES
    ${D}      ${4}    e          ignore_case=Values
    ${D}      ${4}    E          ignore_case=value
    ${D}      ß       Straße     ignore_case=value
    ${D}      ß       strasse    ignore_case=value
    ${D}      list    ${{['A', 'b']}}
    ...                          ignore_case=value
    ${D}      ss      Strasse    ignore_case=value

### Should Contain Sub Dictionary ###

Should contain sub dictionary
    [Template]    Dictionary Should Contain Sub Dictionary
    ${D}    ${{{}}}
    ${D}    ${{{'a': 'x', 'c': 3, 'list': ['a', 'B']}}}
    ${D}    ${D}

Should contain sub dictionary with missing keys
    [Documentation]    FAIL    Following keys missing from first dictionary: 'bad' and '666'
    Dictionary Should Contain Sub Dictionary    ${D}    ${{{'a': 'x', 'bad': 3, 666: None}}}

Should contain sub dictionary with missing keys and custom error message
    [Documentation]    FAIL    The message.
    Dictionary Should Contain Sub Dictionary    ${D}    ${{{'x': 'a'}}}    The message.    False

Should contain sub dictionary with missing keys and custom error message containig values
    [Documentation]    FAIL
    ...    The message.
    ...    Following keys missing from first dictionary: 'x'
    Dictionary Should Contain Sub Dictionary    ${D}    ${{{'x': 'a'}}}    The message.

Should contain sub dictionary with wrong value
    [Documentation]    FAIL
    ...    Following keys have different values:
    ...    Key a: x != bad
    ...    Key c: 3 (integer) != 3 (string)
    Dictionary Should Contain Sub Dictionary    ${D}    ${{{'a': 'bad', 'c': '3'}}}

Should contain sub dictionary with wrong value and custom error message
    [Documentation]    FAIL    The error.
    Dictionary Should Contain Sub Dictionary    ${D}    ${{{'a': 'bad', 'c': '3'}}}    The error.    no values

Should contain sub dictionary with wrong value and custom error message containing values
    [Documentation]    FAIL
    ...    The error.
    ...    Following keys have different values:
    ...    Key a: x != bad
    ...    Key c: 3 (integer) != 3 (string)
    Dictionary Should Contain Sub Dictionary    ${D}    ${{{'a': 'bad', 'c': '3'}}}    The error.

Should contain sub dictionary with `ignore_case`
    [Documentation]    FAIL    Following keys missing from first dictionary: 'ss' and 'non'
    [Template]    Dictionary Should Contain Sub Dictionary
    ${D}    ${{{'A': 'X', 'b': 'y', 'c': 3, 'ss': 'STRASSE'}}}    ignore_case=True
    ${D}    ${{{'list': ['A', 'b'], ('a', 'B'): 'TUPLE'}}}        ignore_case=value
    ${D}    ${{{'ss': 'Straße', ('A', 'b'): 'tuple'}}}            ignore_case=key
    ${D}    ${{{'a': 'x', 'ss': 'Straße', 'non': 'existing'}}}    ignore_case=value

### Misc ###

`ignore_case` when normalized keys have conflict
    VAR    ${expected}
    ...    Dictionary {'a': 1, 'A': 2} contains multiple keys that are normalized to 'a'.
    ...    Try normalizing only dictionary values like 'ignore_case=values'.
    FOR    ${kw}    IN
    ...    Dictionary Should Contain Key
    ...    Dictionary Should Not Contain Key
    ...    Dictionary Should Contain Value
    ...    Dictionary Should Not Contain Value
    ...    Dictionary Should Contain Item
        TRY
            Run Keyword    ${kw}    ${{{'a': 1, 'A': 2}}}    xxx    yyy    ignore_case=True
        EXCEPT    AS    ${err}
            Should Be Equal    ${err}   ${expected}
        ELSE
            Fail    Expected error did not occur.
        END
    END
    TRY
        Dictionary Should Contain Sub Dictionary    ${D}    ${{{'a': 1, 'A': 2}}}    ignore_case=True
    EXCEPT    AS    ${err}
        Should Be Equal    ${err}   ${expected}
    ELSE
        Fail    Expected error did not occur.
    END

`has_key` is not required
    ${dict} =    Get Dict Without Has Key    name=value
    Dictionary Should Contain Key               ${dict}    name
    Dictionary Should Not Contain Key           ${dict}    nonex
    Dictionary Should Contain Item              ${dict}    name    value
    Dictionary Should Contain Sub Dictionary    ${dict}    ${dict}
    Dictionaries Should Be Equal                ${dict}    ${dict}
