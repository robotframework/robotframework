*** Settings ***
Library           newstyleclasses.NewStyleClassLibrary
Library           newstyleclasses.MetaClassLibrary

*** Test Cases ***
Keyword From New Style Class Library
    ${ret} =    Mirror    Hello
    Should Be Equal    ${ret}    olleH

Keyword From Library With Metaclass
    ${greeting} =    Greet    Robot
    Should Be Equal    ${greeting}    Hello Robot!

Keyword Created By Metaclass
    ${foo} =    Kw Created By Metaclass    word
    Should Be Equal    ${foo}    WORD

Methods in Metaclass Are not Keywords
    [Documentation]    FAIL No keyword with name 'Method In Metaclass' found.
    Method In Metaclass
