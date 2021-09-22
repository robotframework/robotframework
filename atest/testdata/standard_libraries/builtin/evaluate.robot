*** Settings ***
Suite Setup       Evaluate    sys.path.append(r'${CURDIR}')
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
    ${world} =    Evaluate    [item for item in $HELLO]
    Should Be Equal    ${hello}    ${world}
    ${len} =    Evaluate    len(@{HELLO})
    Should Be Equal    ${len}    ${2}
    ${hello2} =    Evaluate    'hello'.capitalize() + ' ' + 'world'
    Should Be Equal    ${hello2}    Hello world
    ${stat} =    Evaluate    "${hello2}" == ' '.join(@{HELLO})
    Should Be Equal    ${stat}    ${True}
    Evaluate    INVALID

Modules are imported automatically
    ${ceil} =    Evaluate    math.ceil(1.001)
    Should Be Equal    ${ceil}    ${2}
    ${random} =    Evaluate    random.randint(0, sys.maxsize)
    ${maxint}    ${sep}    ${+} =    Evaluate    sys.maxsize, os.sep, re.escape('+')
    Should Be True    0 <= ${random} <= ${maxint}
    Should Be Equal    ${sep}    ${/}
    Should Be Equal    ${+}    \\+
    ${version} =    Evaluate    robot.__version__.split('.')[0]
    Should Be True    ${version} in (3, 4, 5)

Importing non-existing module fails with NameError
    [Documentation]    FAIL
    ...    Evaluating expression 'nonex' failed: \
    ...    NameError: name 'nonex' is not defined nor importable as module
    Evaluate    nonex

Importing invalid module fails with original error
    [Documentation]    FAIL
    ...    Evaluating expression 'invalidmod' failed: \
    ...    TypeError: This module cannot be imported!
    Evaluate    invalidmod

Automatic module imports are case-sensitive
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Evaluating expression 'OS.sep' failed: \
    ...    NameError: name 'OS' is not defined nor importable as module
    ...
    ...    2) Evaluating expression 'os.sep + OS.sep' failed: \
    ...    NameError: name 'OS' is not defined nor importable as module
    [Template]    Evaluate
    OS.sep
    os.sep + OS.sep

Automatic modules don't override builtins
    ${result} =    Evaluate    len('foo')   # `len.py` exists in this directory
    Should Be Equal    ${result}    ${3}

Explicit modules
    [Documentation]    FAIL REGEXP:
    ...    Evaluating expression 'True' failed: \
    ...    (ModuleNotFound|Import)Error: [Nn]o module named .*
    ${ceil} =    Evaluate    math.ceil(1.001)    math
    Should Be Equal    ${ceil}    ${2}
    ${random} =    Evaluate    random.randint(0, sys.maxsize)    modules=random, sys
    ${maxint}    ${sep}    ${x}    ${y} =    Evaluate    sys.maxsize, os.sep, re.escape('+'), r'\\+'    sys, re,,,,,glob, os,robot,,,
    Should Be True    0 <= ${random} <= ${maxint}
    Should Be Equal    ${sep}    ${/}
    Should Be Equal    ${x}    ${y}
    Evaluate    True    nonex_module

Explicit modules are needed with nested modules
    Run Keyword And Expect Error
    ...    GLOB: Evaluating expression 'rootmod.intermediate.leaf.attribute' failed: AttributeError: *
    ...    Evaluate    rootmod.intermediate.leaf.attribute
    Run Keyword And Expect Error
    ...    GLOB: Evaluating expression 'rootmod.intermediate.leaf.attribute' failed: AttributeError: *
    ...    Evaluate    rootmod.intermediate.leaf.attribute    modules=rootmod
    Run Keyword And Expect Error
    ...    GLOB: Evaluating expression 'rootmod.intermediate.leaf.attribute' failed: AttributeError: *
    ...    Evaluate    rootmod.intermediate.leaf.attribute    modules=rootmod.intermediate
    ${value} =    Evaluate    rootmod.intermediate.leaf.attribute    modules=rootmod.intermediate.leaf
    Should Be Equal    ${value}    ${42}

Explicit modules can override builtins
    ${result} =    Evaluate    len.value    modules=len
    Should Be Equal    ${result}    ${42}
    ${result} =    Evaluate    len('value')
    Should Be Equal    ${result}    ${5}

Explicit modules used in lambda
    ${result} =    Evaluate    ''.join(filter(lambda s: re.match('^He',s), $HELLO))    modules=re
    Should Be Equal    ${result}    Hello

Custom namespace
    ${ns} =    Create Dictionary    a=x    b=${2}    c=2
    ${result} =    Evaluate    a*3 if b==2 and c!=2 else a    namespace=${ns}
    Should Be Equal    ${result}    xxx
    ${result} =    Evaluate    math.pow(b, 3)    math    ${ns}
    Should Be Equal    ${result}    ${8}

Custom namespace is case-sensitive
    [Documentation]    FAIL
    ...    Evaluating expression 'B' failed: \
    ...    NameError: name 'B' is not defined nor importable as module
    ${ns} =    Create Dictionary    a=x    A=y    b=z
    ${result} =    Evaluate    a + A + b    namespace=${ns}
    Should Be Equal    ${result}    xyz
    Evaluate    B    namespace=${ns}

Custon namespace used in lambda
    ${ns} =    Create Dictionary    alphabet=aAbBcCdDeEfFgGhHiIjJkKlLmMnNoO    input=Hello
    ${sorted} =    Evaluate    ''.join(sorted(input, key=lambda word: [alphabet.find(c) for c in word]))     namespace=${ns}
    Should Be Equal    ${sorted}    eHllo

Namespace from Get Variables
    ${foo} =    Set variable    value
    ${ns} =    Get variables    no_decoration=Yes
    ${res} =    Evaluate     foo == 'value'    namespace=${ns}
    Should be Equal    ${res}    ${True}

Non-dict namespace
    ${ns} =    Get user dict   foo=value
    ${res} =    Evaluate     foo == 'value'    namespace=${ns}
    Should be Equal    ${res}    ${True}

Variables are available automatically
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
    [Documentation]    FAIL
    ...    Evaluating expression '$i_do_not_exit and $nor_do_i' failed: \
    ...    Variable '$i_do_not_exit' not found.
    Evaluate    $i_do_not_exit and $nor_do_i

Non-existing automatic variable with recommendation 1
    [Documentation]    FAIL
    ...    Evaluating expression '$HILLO' failed: \
    ...    Variable '$HILLO' not found. Did you mean:
    ...    ${SPACE * 4}$HELLO
    Evaluate    $HILLO

Non-existing automatic variable with recommendation 2
    [Documentation]    FAIL
    ...    Evaluating expression '$hels in $ki' failed: \
    ...    Variable '\$hels' not found. Did you mean:
    ...    ${SPACE * 4}$hell
    ...    ${SPACE * 4}$HELLO
    ${hell} =    Set Variable    xxx
    Evaluate    $hels in $ki

Invalid expression 1
    [Documentation]    FAIL STARTS: Evaluating expression 'oooops' failed: NameError:
    Evaluate   oooops

Invalid expression 2
    [Documentation]    FAIL STARTS: Evaluating expression 'Someone forgot to add quotes!' failed: SyntaxError:
    Evaluate    Someone forgot to add quotes!

Invalid expression 3
    [Documentation]    FAIL STARTS: Evaluating expression 'We have\nmultiple\nlines' failed: SyntaxError:
    Evaluate    We have\nmultiple\nlines

Invalid expression 4
    [Documentation]    FAIL STARTS: Evaluating expression '1/0' failed: ZeroDivisionError:
    Evaluate   1/0

Invalid expression 5
    [Documentation]    FAIL STARTS: Evaluating expression '(1, 2' failed: SyntaxError:
    Evaluate   (1, 2

Invalid expression 6
    [Documentation]    FAIL STARTS: Evaluating expression 'len(None)' failed: TypeError:
    Evaluate   len(None)

Invalid expression 7
    [Documentation]    FAIL STARTS: Evaluating expression '[][0]' failed: IndexError:
    Evaluate   [][0]

Invalid expression 8
    [Documentation]    FAIL STARTS: Evaluating expression '{}[0]' failed: KeyError:
    Evaluate   {}[0]

Invalid $ usage 1
    [Documentation]    FAIL STARTS: Evaluating expression '$' failed: SyntaxError:
    Evaluate   $

Invalid $ usage 2
    [Documentation]    FAIL STARTS: Evaluating expression '$$' failed: SyntaxError:
    Evaluate   $$

Invalid $ usage 3
    [Documentation]    FAIL STARTS: Evaluating expression '$$hello' failed: SyntaxError:
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
    [Documentation]    FAIL STARTS: Evaluating expression 'raise $HELLO' failed: SyntaxError:
    Evaluate    raise $HELLO

Invalid $ usage 8
    [Documentation]    FAIL STARTS: Evaluating expression '$HELLO $' failed: SyntaxError:
    Evaluate    $HELLO $

Evaluate Empty
    [Documentation]    FAIL Evaluating expression '' failed: ValueError: Expression cannot be empty.
    Evaluate    ${EMPTY}

Evaluate Nonstring
    [Documentation]    FAIL Evaluating expression '5' failed: TypeError: Expression must be string, got integer.
    Evaluate    ${5}

Evaluate doesn't see module globals
    [Documentation]    FAIL STARTS: Evaluating expression 'DataError' failed: NameError:
    Evaluate    DataError

Evaluation errors can be caught
    FOR    ${invalid}    IN    ooops    1/0    $    $nonex    len(None)    ${EMPTY}    ${7}
        ${err1} =                 Run Keyword And Expect Error    *    Evaluate    ${invalid}
        ${status}    ${err2} =    Run Keyword And Ignore Error         Evaluate    ${invalid}
        Should Be Equal    ${status}    FAIL
        Should Be Equal    ${err1}    ${err2}
    END
