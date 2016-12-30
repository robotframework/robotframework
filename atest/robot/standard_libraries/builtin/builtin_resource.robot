*** Settings ***
Resource          atest_resource.robot

*** Keywords ***
Verify argument type message
    [Arguments]    ${msg}    ${type1}    ${type2}
    ${type1} =    Map String Types    ${type1}
    ${type2} =    Map String Types    ${type2}
    ${level} =    Evaluate   'DEBUG' if $type1 == $type2 else 'INFO'
    Check log message    ${msg}    Argument types are:\n<* '${type1}'>\n<* '${type2}'>    ${level}    pattern=True

Map String Types
    [Arguments]    ${type}
    Return From Keyword If    ($INTERPRETER.is_py2 and not $INTERPRETER.is_ironpython) and $type == "bytes"    str
    Return From Keyword If    ($INTERPRETER.is_py3 or $INTERPRETER.is_ironpython) and $type == "str"    unicode
    Return From Keyword    ${type}
