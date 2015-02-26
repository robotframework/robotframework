*** Settings ***
Suite Setup       Set lxml availability to suite metadata
Library           XML    use_lxml=yes
Resource          xml_resource.robot

*** Test Cases ***
Elements Are Mutable
    ${xml} =    Parse XML    <root><child/></root>
    ${child} =    Get Element    ${xml}    child
    Set Element Attribute    ${child}    a    1
    Set Element Text    ${xml}    text    xpath=child
    Elements Should Be Equal    ${child}    <child a="1">text</child>
    Elements Should Be Equal    ${xml}    <root><child a="1">text</child></root>

Copy Element
    ${xml} =    Parse XML    <root><child/></root>
    ${child} =    Get Element    ${xml}    xpath=child
    ${child} =    Copy Element    ${child}
    Set Element Attribute    ${child}    a    1
    Set Element Text    ${xml}    text    xpath=child
    Elements Should Be Equal    ${child}    <child a="1"/>
    Elements Should Be Equal    ${xml}    <root><child>text</child></root>

Copy Element Using Xpath
    ${xml} =    Parse XML    <root><child/></root>
    ${child} =    Copy Element    ${xml}    xpath=child
    Set Element Attribute    ${child}    a    1
    Set Element Text    ${xml}    text    xpath=child
    Elements Should Be Equal    ${child}    <child a="1"/>
    Elements Should Be Equal    ${xml}    <root><child>text</child></root>

Copy Deeper Structure
    ${xml} =    Parse XML    ${TEST}
    ${copy} =    Copy Element    ${xml}    xpath=another
    Set Element Text    ${copy}    new    xpath=child
    Element Text Should Be    ${xml}    nöŋ-äŝĉíï tëxt    xpath=another/child
