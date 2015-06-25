*** Settings ***
Library           Collections

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
    [Documentation]    FAIL REGEXP: ImportError: [Nn]o module named nonex_module
    ${ceil} =    Evaluate    math.ceil(1.001)    math
    Should Be Equal    ${ceil}    ${2}
    ${random} =    Evaluate    random.randint(0, sys.maxint)    modules=random,sys
    ${maxint}    ${sep}    ${x}    ${y} =    Evaluate    sys.maxint, os.sep, re.escape('+'), '\\+'    sys, re,,,,, glob, os,robot,,,
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
    ${ns} =    Evaluate    UserDict.UserDict(foo='value')    modules=UserDict
    ${res} =    Evaluate     foo == 'value'    namespace=${ns}
    Should be Equal    ${res}    ${True}

Evaluate gets Variables automatically
    ${foo} =    Set variable    value
    ${res} =    Evaluate     foo == 'value'
    Should be Equal    ${res}    ${True}

Variables don't override python builtins
    ${len} =    Set variable    value
    ${bar} =    Set variable    something
    ${res} =    Evaluate     len(bar)
    Should be Equal    ${res}    ${9}

Variables don't override custom namespace
    ${ns} =    Create Dictionary    a=VISIBLE
    ${a} =    Set variable    NOT VISIBLE
    ${res} =    Evaluate     a == 'VISIBLE'   namespace=${ns}
    Should be Equal    ${res}    ${True}

Variables don't override modules
    ${posixpath} =    Set variable    NOT VISIBLE
    ${sys} =    Set variable    VISIBLE
    ${res} =    Evaluate    posixpath.join(sys, sys)    modules=posixpath
    Should be Equal    ${res}    VISIBLE/VISIBLE

Variables are case and underscore insensitive
    ${foo} =    Set variable    value
    ${foo with space} =    Set variable    value with space
    ${res} =    Evaluate     FOO == 'value' and FOO_with_SPACE == 'value with space'
    Should be Equal    ${res}    ${True}

Evaluate Empty
    [Documentation]    FAIL Evaluating expression '' failed: ValueError: Expression cannot be empty.
    Evaluate    ${EMPTY}

Evaluate Nonstring
    [Documentation]    FAIL Evaluating expression '5' failed: TypeError: Expression must be string, got integer.
    ${nonstring}=    Evaluate    5
    Evaluate    ${nonstring}
