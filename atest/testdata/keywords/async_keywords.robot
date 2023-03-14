*** Settings ***
Library          AsyncLib.py

*** Test Cases ***
Works With Asyncio Run
    ${result} =    Async With Run Inside
    Should Be Equal    ${result}    Works

Basic Async Works
    ${result} =    Basic Async Test
    Should Be Equal    ${result}    Got it

Works Using Gather
    Can Use Gather

Long Async Tasks Run In Background
    ${hanger} =     Create Hanger
    Basic Async Test
    Stop task From Hanger   ${hanger}
    ${size} =    Evaluate    len($hanger.ticks)
    Should Be True    ${size} > 1

Builtin Call From Library Works
    ${result} =    Run Keyword Using Builtin
    Should Be Equal    ${result}    Got it
