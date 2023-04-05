*** Settings ***
Library          AsyncLib.py

*** Test Cases ***
Works With Asyncio Run
    [Tags]    require-py3.7
    ${result} =    Async With Run Inside
    Should Be Equal    ${result}    Works

Basic Async Works
    ${result} =    Basic Async Test
    Should Be Equal    ${result}    Got it

Works Using Gather
    Can Use Gather

Long Async Tasks Run In Background
    [Tags]    require-py3.7
    ${hanger} =     Create Hanger
    Basic Async Test
    Stop task From Hanger   ${hanger}
    ${size} =    Evaluate    len($hanger.ticks)
    Should Be True    ${size} > 1

Builtin Call From Library Works
    ${result} =    Run Keyword Using Builtin
    Should Be Equal    ${result}    Got it

Create Task With Loop Reference
    ${result} =    Create Task With Loop
    Should Be Equal    ${result}    Got it

Generators Do Not Use Event Loop
    ${generator} =    Evaluate    (i for i in range(5))
    Should Be Equal    ${{sum($generator)}}    ${10}
    Should Be Equal    ${{sum($generator)}}    ${0}
