*** Settings ***
Library           Collections
Library           get_user_dict.py

*** Variables ***
@{HELLO}          Hello    world

*** Test Cases ***
Evaluate
    [Documentation]    FAIL STARTS: Evaluating expression 'INVALID' failed: NameError:
    ${stat} =    Evaluate    True
    Should Be Equal    ${stat}    ${True}
    ${n} =    Evaluate    None
    Should Be Equal    ${n}    ${None}
    ${ten} =    Evaluate    100 - 9*11 + int(9.9)
    Should Be Equal    ${ten}    ${10}
    ${dict} =    Evaluate    {'a': 1, 'b': 2, 'c': 3}
    Should Be True    ${dict['a']} + ${dict['b']} == ${dict['c']}
    ${len} =    Evaluate    len(@{HELLO})
    Should Be Equal    ${len}    ${2}
    ${hello2} =    Evaluate    'hello'.capitalize() + ' ' + 'world'
    Should Be Equal    ${hello2}    Hello world
    ${stat} =    Evaluate    "${hello2}" == ' '.join(@{HELLO})
    Should Be Equal    ${stat}    ${True}
    Evaluate    INVALID

Evaluate With Modules
    [Documentation]    FAIL REGEXP: ImportError: [Nn]o module named .*
    ${ceil} =    Evaluate    math.ceil(1.001)    math
    Should Be Equal    ${ceil}    ${2}
    ${random} =    Evaluate    random.randint(0, sys.maxsize)    modules=random,sys
    ${maxint}    ${sep}    ${x}    ${y} =    Evaluate    sys.maxsize, os.sep, re.escape('+'), '\\+'    sys, re,,,,, glob, os,robot,,,
    Should Be True    0 <= ${random} <= ${maxint}
    Should Be Equal    ${x}    ${y}
    Evaluate    1    nonex_module

Evaluate With Namespace
    ${ns} =    Create Dictionary    a=x    b=${2}    c=2
    ${result} =    Evaluate    a*3 if b==2 and c!=2 else a    namespace=${ns}
    Should Be Equal    ${result}    xxx
    ${result} =    Evaluate    math.pow(b, 3)    math    ${ns}
    Should Be Equal    ${result}    ${8}

Evaluate with Get Variables Namespace
    ${foo} =    Set variable    value
    ${ns} =    Get variables    no_decoration=Yes
    ${res} =    Evaluate     foo == 'value'    namespace=${ns}
    Should be Equal    ${res}    ${True}

Evaluate with Non-dict Namespace
    ${ns} =    Get user dict   foo=value
    ${res} =    Evaluate     foo == 'value'    namespace=${ns}
    Should be Equal    ${res}    ${True}

Evaluate gets variables automatically
    ${foo} =    Set variable    value
    ${res} =    Evaluate     $foo == 'value'
    Should be Equal    ${res}    ${True}

Automatic variables don't work in strings
    ${foo} =    Set variable    value
    ${res} =    Evaluate     '$foo'
    Should be Equal    ${res}    $foo

Automatic variables don't override Python built-ins
    ${len} =    Set variable    value
    ${res} =    Evaluate     len($len)
    Should be Equal    ${res}    ${5}

Automatic variables don't override custom namespace
    ${ns} =    Create Dictionary    key=value 1
    ${key} =    Set variable    value 2
    ${res} =    Evaluate    key == 'value 1' and $key == 'value 2'    namespace=${ns}
    Should be Equal    ${res}    ${True}

Automatic variables don't override modules
    ${posixpath} =    Set variable    xxx
    ${res} =    Evaluate    posixpath.join($posixpath, $posixpath)    modules=posixpath
    Should be Equal    ${res}    xxx/xxx

Automatic variables are case and underscore insensitive
    ${foo} =    Set variable    value
    ${foo with space} =    Set variable    value with space
    ${res} =    Evaluate     $FOO == 'value' and $FOO_with_SPACE == 'value with space'
    Should be Equal    ${res}    ${True}

Automatic variable from variable
    ${auto} =    Set variable    $hello
    ${result} =    Evaluate    ' '.join(${auto})
    Should be Equal    ${result}    Hello world

Non-existing automatic variable
    [Documentation]    FAIL Variable '$i_do_not_exit' not found.
    Evaluate    $i_do_not_exit

Non-existing automatic variable with recommendation 1
    [Documentation]    FAIL Variable '$HILLO' not found. Did you mean:\n${SPACE * 4}$HELLO
    Evaluate    $HILLO

Non-existing automatic variable with recommendation 2
    [Documentation]    FAIL Variable '\$hell' not found. Did you mean:\n${SPACE * 4}$HELLO\n${SPACE * 4}$hella
    ${hella} =    Set Variable    xxx
    Evaluate    $hell

Invalid $ usage 1
    [Documentation]    FAIL STARTS: Evaluating expression '$' failed: SyntaxError:
    Evaluate   $

Invalid $ usage 2
    [Documentation]    FAIL STARTS: Evaluating expression '$$' failed: SyntaxError:
    Evaluate   $$

Invalid $ usage 3
    [Documentation]    FAIL STARTS: Evaluating expression '$RF_VAR_hello' failed: SyntaxError:
    Evaluate   $$hello

Invalid $ usage 4
    [Documentation]    FAIL STARTS: Evaluating expression 'len($)' failed: SyntaxError:
    Evaluate    len($)

Invalid $ usage 5
    [Documentation]    FAIL STARTS: Evaluating expression '$""' failed: SyntaxError:
    Evaluate    $""

Invalid $ usage 6
    [Documentation]    FAIL STARTS: Evaluating expression '"" $' failed: SyntaxError:
    Evaluate    "" $

Invalid $ usage 7
    [Documentation]    FAIL REGEXP: Evaluating expression 'raise +RF_VAR_HELLO' failed: SyntaxError: .*
    Evaluate    raise $HELLO

Invalid $ usage 8
    [Documentation]    FAIL REGEXP: Evaluating expression 'RF_VAR_HELLO  +\\$' failed: SyntaxError: .*
    Evaluate    $HELLO $

Evaluate Empty
    [Documentation]    FAIL Evaluating expression '' failed: ValueError: Expression cannot be empty.
    Evaluate    ${EMPTY}

Evaluate Nonstring
    [Documentation]    FAIL Evaluating expression '5' failed: TypeError: Expression must be string, got integer.
    Evaluate    ${5}

Evaluate doesn't see module globals
    [Documentation]    FAIL Evaluating expression 'BuiltIn' failed: NameError: name 'BuiltIn' is not defined
    Evaluate    BuiltIn
