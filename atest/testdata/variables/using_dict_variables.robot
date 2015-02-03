*** Settings ***
Library      Collections
Variables    dict_vars.py

*** Variables ***
&{DICT}      a=1    b=${2}    c=3
&{ESCAPED}   \${a}=c:\\temp    b=\${2}    ${/}=${\n}    4\=5\\\=6=value
&{ONE}       ${1}=${1}
@{LIST}      one    two    three


*** Test Cases ***
From variable table
    ${result} =    Create Dictionary    &{DICT}
    Dictionaries Should Be Equal    ${result}    ${DICT}

From variable file
    ${result} =    Create Dictionary    &{DICT FROM VAR FILE}
    Dictionaries Should Be Equal    ${result}    ${DICT}

From keyword return value
    ${return} =    Create Dictionary    a=1    b=${2}    c=3
    ${result} =    Create Dictionary    &{return}
    Dictionaries Should Be Equal    ${result}    ${DICT}

Escaped dict
    ${var} =    Set Variable    \&{DICT}
    Should Be Equal    ${var}    \&{DICT}

Escaped items in dict
    ${expected} =    Create Dictionary    \${a}=c:\\temp    b=\${2}    ${/}=${\n}    4\=5\\\=6=value
    Dictionaries Should Be Equal    ${ESCAPED}    ${expected}
    ${result} =    Create Dictionary    &{ESCAPED}
    Dictionaries Should Be Equal    ${result}    ${expected}

Multiple dict variables
    ${1st} =    Create Dictionary    a=1    b=2    c=3
    ${2nd} =    Create Dictionary
    ${3rd} =    Create Dictionary    d=4
    ${result} =    Create Dictionary    &{1st}    &{2nd}    &{3rd}
    ${expected} =    Create Dictionary    a=1    b=2    c=3    d=4
    Dictionaries Should Be Equal    ${result}    ${expected}

Multiple dict variables with same names multiple times
    ${1st} =    Create Dictionary    a=1    b=1    c=1    d=1
    ${2nd} =    Create Dictionary    b=2    c=2    d=2
    ${3rd} =    Create Dictionary    c=3    d=2
    ${result} =    Create Dictionary    d=0    &{1st}    &{2nd}    &{3rd}    d=4
    ${expected} =    Create Dictionary    a=1    b=2    c=3    d=4
    Dictionaries Should Be Equal    ${result}    ${expected}

Internal variables
    ${d}    ${i}    ${c}    ${t} =    Create List    d    i    c    t
    ${result} =    Create Dictionary    &{${d}${i}${c}${t}}
    Dictionaries Should Be Equal    ${result}    ${DICT}
    ${result} =    Create Dictionary    &{${i[${1}:]} ${d} ${i + 'ct'}}
    Dictionaries Should Be Equal    ${result}    ${DICT}

Extended variables
    ${result} =    Create Dictionary    &{CLASS FROM VAR FILE.attribute}
    Dictionaries Should Be Equal    ${result}    ${DICT}
    ${result} =    Create Dictionary    &{OBJECT FROM VAR FILE.attribute}
    Dictionaries Should Be Equal    ${result}    ${DICT}
    ${result} =    Create Dictionary    &{OBJECT FROM VAR FILE.get_escaped()}
    Dictionaries Should Be Equal    ${result}    ${ESCAPED}

Converted to string if not alone
    Should Be Equal    ---&{ONE}---    ---{1: 1}---
    Should Be Equal    &{ONE}${ONE}    {1: 1}{1: 1}
    Should Be Equal    &{ONE}}}}}}}    {1: 1}}}}}}}
    Should Be Equal    &&&&&&&{ONE}    &&&&&\&{1: 1}
    Should Be Equal    &&&&{ONE}}}}    &&\&{1: 1}}}}
    ${result} =    Create Dictionary    &{ONE}}=&{ONE}    &{ONE}\==&{ONE}}
    ${value1} =    Get From Dictionary    ${result}    &{ONE}}
    ${value2} =    Get From Dictionary    ${result}    &{ONE}=
    Should Be Equal    ${value1}    ${ONE}
    Should Be Equal    ${value2}    &{ONE}}

Non-existing
    [Documentation]    FAIL Variable '&{non existing}' not found.
    Create Dictionary    &{non existing}

Non-dictionary
    [Documentation]    FAIL Value of variable '\&{LIST}' is not dictionary or dictionary-like.
    Create Dictionary    &{LIST}

Non-string keys
    [Documentation]    FAIL Argument names must be strings.
    ${ints} =    Evaluate    {1: 2, 3: 4}
    Create Dictionary    &{ints}
