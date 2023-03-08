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

Builtin Async Sleep Keyword Works
    Async Sleep    1s    Testing async sleep

Long Async Tasks Run In Background
    ${hanger} =     Create Hanger
    Async Sleep    2s    Normal sleep blocks thread, need async sleep to work
    Stop task From Hanger   ${hanger}
    ${size} =    Evaluate    len($hanger.ticks)
    Should Be True    ${size} > 1

Builtin Call From Library Works
    ${result} =    Run Keyword Using Builtin
    Should Be Equal    ${result}    Got it

Builtin Gather Keyword Works
    ${result} =    Gather Async Keywords    Basic Async Test    Basic Async Test    Basic Async Test
    ${list} =   Create List    Got it    Got it    Got it
    Should Be Equal    ${result}    ${list}

Builtin Gather Keyword Fails If Keyword Is Not Async
    [Documentation]    FAIL
    ${result} =    Gather Async Keywords    Basic Async Test    No Operation
