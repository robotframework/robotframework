*** Settings ***
Suite Setup       Set lxml availability to suite metadata
Library           XML    use_lxml=yes
Resource          xml_resource.robot

*** Variables ***
${WITH TAIL}    <root a="v"><child a="v">text</child>tail</root>

*** Test Cases ***
Clear Element
    ${xml} =    Parse XML    ${TEST}
    Clear Element    ${xml}
    Elements Should Be Equal    ${xml}    <test/>

Clear Element Returns Root Element
    ${root} =    Clear Element    ${SIMPLE}    xpath=child
    ${root} =    Clear Element    ${root}    xpath=c2
    Elements Should Be Equal    ${root}    <root><child/><c2/></root>

Tail Text Is Not Cleared By Default
    ${root} =    Clear Element    ${WITH TAIL}    xpath=child
    Elements Should Be Equal    ${root}    <root a="v"><child/>tail</root>

Tail Text Can Be Cleared
    ${root} =    Clear Element    ${WITH TAIL}    child    clear_tail=false
    Elements Should Be Equal    ${root}    <root a="v"><child/>tail</root>
    ${root} =    Clear Element    ${WITH TAIL}    child    clear_tail=yes
    Elements Should Be Equal    ${root}    <root a="v"><child/></root>
