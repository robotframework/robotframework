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
    ${hello} =    Evaluate    'hello'.capitalize() + ' ' + 'world'
    Should Be Equal    ${hello}    Hello world
    ${stat} =    Evaluate    "${hello}" == ' '.join(@{HELLO})
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
