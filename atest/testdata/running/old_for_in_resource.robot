*** Settings ***
Library         String

*** Keywords ***
Old for loop in resource
    :FOR    ${value}    IN    This    is    deprecated!!!
    \    ${value} =    Convert to upper case    ${value}
    Should be equal    ${value}    DEPRECATED!!!
