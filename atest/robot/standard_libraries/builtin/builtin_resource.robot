*** Settings ***
Resource          atest_resource.robot

*** Keywords ***
Verify argument type message
    [Arguments]    ${msg}    ${type1}    ${type2}
    ${level} =    Evaluate   'DEBUG' if $type1 == $type2 else 'INFO'
    Check log message    ${msg}    Argument types are:\n<* '${type1}'>\n<* '${type2}'>    ${level}    pattern=True
