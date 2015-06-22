*** Settings ***
Documentation    Tests ET's XPATH support documented at
...              http://effbot.org/zone/element-xpath.htm
...              Notice that '..', predicates ('[stuff]'), and more complex
...              expressions with non-ASCII characters require ET 1.3
...              (i.e. interpreter version 2.7) or newer.
Library          XML    use_lxml=False
Resource         xml_resource.robot
Suite Setup      Add Etree Version to Suite Metadata
Test Template    Xpath should match element

*** Test Cases ***
Tag
    another    another

Path
    another/child    child    nöŋ-äŝĉíï tëxt

Path matching multiple elements
    [Template]    Xpath should match elements
    child               child 1 text    child 2 text grand child text more text    ${EMPTY}
    child/grandchild    grand child text    ${EMPTY}

'*'
    */child    child    nöŋ-äŝĉíï tëxt

'.'
    .    test
    ./another    another

'//'
    .//ggc    ggc
    .//grandchild/ggc    ggc
    child//ggc    ggc
    another//child    child

'//' matching multiple elements
    [Template]    Xpath should match elements
    .//child               child 1 text    child 2 text grand child text more text    ${EMPTY}    nöŋ-äŝĉíï tëxt
    .//child/grandchild    grand child text    ${EMPTY}

'..'
    another/..    test
    another/child/..    another
    .//ggc/..    grandchild
    another/child/../../child[@id="3"]  child

'[@attrib]'
    [Documentation]    FAIL No element matching 'child[@nonex]' found.
    child[@a2]    child    ${NONE}
    child[@nonex]    not-found

'[@attrib="value"]'
    [Documentation]    FAIL No element matching 'child[@id="xxx"]' found.
    child[@id="2"]    child    \n${SPACE*8}child 2 text\n${SPACE*8}
    child[@a2='xxx']    child    ${NONE}
    child[@id="xxx"]    not-found

'[tag]'
    [Documentation]    FAIL No element matching 'child[nonex]' found.
    another[child]    another
    */grandchild[ggc]    grandchild
    child[nonex]    not-found

'[position]'
    [Documentation]    FAIL No element matching 'child[4]' found.
    child[1]    child    child 1 text
    child[3]    child    ${NONE}
    child[4]    not-found

Stacked predicates
    child[@id][@a3='y']    child    ${NONE}
    child/grandchild[1][ggc]    grandchild    ${NONE}

Non-ASCII tag names
    täg    täg    xml=<rööt><täg/></rööt>
    täg/chïld    chïld    xml=<rööt><täg><chïld/></täg></rööt>

More complex non-ASCII xpath
    [Documentation]    FAIL Multiple elements (2) matching './/chïld' found.
    .//chïld    chïld    xml=<rööt><chïld/><täg><chïld/></täg></rööt>

Evaluate xpath does not work
    [Documentation]    FAIL 'Evaluate Xpath' keyword only works in lxml mode.
    [Template]    NONE
    Evaluate Xpath    ${TEST}    .

*** Keywords ***
Xpath should match element
    [Arguments]    ${xpath}    ${tag}    ${text}=IGNORE    ${xml}=${TEST}
    ${element}=     Get Element    ${xml}    ${xpath}
    Should Be Equal    ${element.tag}    ${tag}
    Run Keyword If    '''${text}''' != 'IGNORE'    Should Be Equal    ${element.text}    ${text}

Xpath should match elements
    [Arguments]    ${xpath}    @{expected texts}
    ${texts} =    Get Elements Texts    ${TEST}    ${xpath}    normalize_whitespace=yes
    Lists Should be Equal    ${texts}    ${expected texts}

Add Etree Version to Suite Metadata
    ${version}=    Get Etree Version
    Set Suite Metadata    ET Version    ${version}
