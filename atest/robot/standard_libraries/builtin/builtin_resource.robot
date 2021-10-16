*** Settings ***
Resource          atest_resource.robot

*** Keywords ***
Verify argument type message
    [Arguments]    ${msg}    ${type1}=str    ${type2}=str
    ${level} =    Evaluate   'DEBUG' if $type1 == $type2 else 'INFO'
    Check log message    ${msg}    Argument types are:\n<class '${type1}'>\n<class '${type2}'>    ${level}
