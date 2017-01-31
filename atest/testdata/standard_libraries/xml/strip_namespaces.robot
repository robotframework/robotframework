*** Settings ***
Library           XML    use_lxml=false
Resource          xml_resource.robot
Test Setup        Parse XML To Test Variable    ${NS}    \${ROOT}    strip_namespaces=True

*** Test Cases ***
Tag names contain no namespaces
    ${children} =    Get Child Elements    ${ROOT}
    Should Be Equal    ${children[0].tag}    child1
    Should Be Equal    ${children[1].tag}    child2
    Should Be Equal    ${children[2].tag}    child3
    Should Be Equal    ${children[3].tag}    another
    Should Be Equal    ${children[4].tag}    back

Namespaces are not needed in xpath
    [Template]    Element Text Should Be
    ${ROOT}    default ns          xpath=child1
    ${ROOT}    ns with prefix      xpath=child2
    ${ROOT}    2nd prefix          xpath=child3/grand-child
    ${ROOT}    1st prefix again    xpath=child3/grand-child-2/ggc
    ${ROOT}    default ns 2        xpath=child3/grand-child-2/ggc2
    ${ROOT}    2nd default         xpath=another/child
    ${ROOT}    back in default     xpath=back

xmlns attributes are not needed
    [Template]    Element Should Not Have Attribute
    ${ROOT}    xmlns    .
    ${ROOT}    xmlns    child1
    ${ROOT}    xmlns    child2
    ${ROOT}    xmlns    child3
    ${ROOT}    xmlns    child3/grand-child
    ${ROOT}    xmlns    child3/grand-child-2
    ${ROOT}    xmlns    child3/grand-child-2/ggc
    ${ROOT}    xmlns    child3/grand-child-2/ggc2
    ${ROOT}    xmlns    child3/grand-child-3
    ${ROOT}    xmlns    another
    ${ROOT}    xmlns    another/child
    ${ROOT}    xmlns    back

Saved XML has correct content and no namespaces
    Saved XML Should Equal    ${ROOT}
    ...    <test name="root">
    ...    ${INDENT}<child1 id="1">default ns</child1>
    ...    ${INDENT}<child2>ns with prefix</child2>
    ...    ${INDENT}<child3>
    ...    ${INDENT}${INDENT}<grand-child>2nd prefix</grand-child>
    ...    ${INDENT}${INDENT}<grand-child-2>
    ...    ${INDENT}${INDENT}${INDENT}<ggc>1st prefix again</ggc>
    ...    ${INDENT}${INDENT}${INDENT}<ggc2>default ns 2</ggc2>
    ...    ${INDENT}${INDENT}</grand-child-2>
    ...    ${INDENT}${INDENT}<grand-child-3>2nd prefix 2</grand-child-3>
    ...    ${INDENT}</child3>
    ...    ${INDENT}<another>
    ...    ${INDENT}${INDENT}<child>2nd default</child>
    ...    ${INDENT}</another>
    ...    ${INDENT}<back>back in default</back>
    ...    </test>
    [Teardown]    Remove Output File

Attribute namespaces are not stripped
    [Setup]    NONE
    ${root} =    Parse XML    ${ATTR NS}    strip_namespaces=true
    Test Attribute Namespace Parsing    ${root}
