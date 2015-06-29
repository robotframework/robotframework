*** Settings ***
Suite Setup       Set lxml availability to suite metadata
Test Template     Xpath should match element
Library           XML    use_lxml=true
Resource          xml_resource.robot

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
    child[2]    child    \n${SPACE*8}child 2 text\n${SPACE*8}
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

Advanced xpath supported by lxml
    child[text() = 'child 1 text']     child         child 1 text
    child[position()=1]                child         child 1 text
    child[position() > 1 and not(position() >= 3)]    child    \n${SPACE*8}child 2 text\n${SPACE*8}
    child[last()]                      child         ${NONE}
    child[last()]/grandchild           grandchild    ${NONE}
    (//child)[last()]                  child         nöŋ-äŝĉíï tëxt
    (child/grandchild)[last()]         grandchild    ${NONE}
    (child | another | xxx)[last()]    another
    self::test                         test
    child::child[1]/parent::test       test
    descendant::ggc/parent::*          grandchild
    descendant::ggc/ancestor::child[attribute::id]    child

Advanced xpath supported by lxml matching multiple elements
    [Template]    Xpath should match elements
    (child | another | xxx)    child 1 text    child 2 text grand child text more text    ${EMPTY}    nöŋ-äŝĉíï tëxt
    child[starts-with(normalize-space(text()), 'child')]
    ...                        child 1 text    child 2 text grand child text more text

Evaluate xpath
    [Template]    Result of evaluation should be
    count(*)                           ${4}
    count(child[3]/descendant::*)      ${2}
    count(preceding-sibling::*)        ${0}
    count(*)                           ${1}            context=child[3]
    count(preceding-sibling::*)        ${2}            context=child[3]
    string(child[1])                   child 1 text
    string()                           child 1 text    context=child[1]
    contains(child[1], '1 text')       ${True}
    string(child::child[last()]/ancestor::test/attribute::name)     root
    string(descendant::ggc/ancestor::child[attribute::id=3]/@a2)    xxx

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

Result of evaluation should be
    [Arguments]    ${xpath}    ${expected}    ${xml}=${TEST}    ${context}=.
    ${result} =    Evaluate xpath    ${xml}    ${xpath}    context=${context}
    Should Be Equal    ${result}    ${expected}
