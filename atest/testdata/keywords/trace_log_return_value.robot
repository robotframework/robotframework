*** Settings ***
Library           NonAsciiLibrary
Library           TraceLogArgsLibrary.py

*** Test Cases ***
Return from Userkeyword
    Return Value From UK

Return from Library Keyword
    Set Variable    value

Return From Run Keyword
    Run Keyword    Set Variable    value

Return Non String Object
    Convert To Integer    1

Return None
    No Operation

Return Non Ascii String
    Set Variable    Hyvää 'Päivää'\n

Return Object With Unicode Repr
    Print and Return NonASCII Object

Return Object with Unicode Repr With Non Ascii Chars
    Return Object With Invalid Repr

Return Object with Non Ascii String from Repr
    Return Object With Non Ascii String Repr

*** Keywords ***
Return Value From UK
    ${return} =    Set Variable    value
    [Return]    ${return}
