*** Settings ***
Library    UnicodeLibrary
Library    TraceLogArgsLibrary


*** Test Cases ***
Return from Userkeyword
    Return Value From UK

Return from Library Keyword
    Set Variable  value

Return From Run Keyword
    Run Keyword  Set Variable  value

Return Non String Object
    Convert To Integer  1

Return None
    No Operation

Return Non Ascii String
    Set Variable  Hyvää Päivää

Return Object With Unicode Repr
    Print and Return Unicode Object

Return Object with Invalid Unicode Repr
    Return Object With Invalid Repr

Return Object with Non Ascii String from Repr
   Return Object With Non Ascii String Repr

*** User Keywords ***
Return Value From UK  [Return]  ${return}
    ${return} =  Set Variable  value
