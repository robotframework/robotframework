*** Settings ***
Library           XML
Resource          xml_resource.robot

*** Variables ***
${TÄG}    <täg attr="hyvä">sisältö</täg>
${XML}    <root>\n\t${TÄG}\n</root>

*** Test Cases ***
Element to string
    ${string}=    Element To String    ${XML}
    Should Be Equal    ${string}    ${XML}
    ${string}=    Element To String    ${TEST}
    Elements Should Be Equal    ${string}    ${TEST}

Child element to string
    ${string}=    Element To String    ${XML}    xpath=täg
    Should Be Equal    ${string}    ${TÄG}

Log element
    ${string}=    Log Element    ${XML}
    Should Be Equal    ${string}    ${XML}
    Log Element    <root><tag a="1" c="3">päivää</tag></root>    DEBUG
    Log Element    ${TEST}

Log child element
    ${string}=    Log Element    ${XML}    xpath=täg
    Should Be Equal    ${string}    ${TÄG}
