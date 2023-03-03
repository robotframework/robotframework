*** Settings ***
Library          Collections
Library          AsyncLib.py

*** Test Cases ***
Basic Async Works
    ${result} =    Basic Async Test
    Should Be Equal    ${result}    Got it

Works With Asyncio Run
    ${result} =    Async With Run Inside
    Should Be Equal    ${result}    Works

Long Async Tasks Run In Background
    ${hanger} =     Create Hanger
    Sleep    2
    Stop task From Hanger   ${hanger}
    ${sub_list} =   Create List    tick    tick
    List Should Contain Sub List    ${hanger.ticks}    ${sub_list}
