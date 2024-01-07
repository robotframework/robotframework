*** Settings ***
Suite Setup       Set lxml availability to suite metadata
Test Setup        Remove File    ${OUTPUT}
Suite Teardown    Remove File    ${OUTPUT}
Library           XML    use_lxml=yes
Resource          xml_resource.robot

*** Test Cases ***
Tag names contain no namespaces
    ${children} =    Get Child Elements    ${NS}
    Should Be Equal    ${children[0].tag}    child1
    Should Be Equal    ${children[1].tag}    child2
    Should Be Equal    ${children[2].tag}    child3
    Should Be Equal    ${children[3].tag}    another
    Should Be Equal    ${children[4].tag}    back

Namespaces are not needed in xpath
    [Template]    Element Text Should Be
    ${NS}    default ns        xpath=child1
    ${NS}    ns with prefix    xpath=child2
    ${NS}    2nd prefix        xpath=child3/grand-child
    ${NS}    1st prefix again  xpath=child3/grand-child-2/ggc
    ${NS}    default ns 2      xpath=child3/grand-child-2/ggc2
    ${NS}    2nd default       xpath=another/child
    ${NS}    back in default   xpath=back

xmlns attributes with default namespaces are added when needed
    [Template]    Element Should Have Attributes
    ${NS}    .    name=root    xmlns=default
    ${NS}    child1    id=1
    ${NS}    child2    xmlns=http://uri
    ${NS}    child3    xmlns=whatever.xsd
    ${NS}    child3/grand-child
    ${NS}    child3/grand-child-2    xmlns=http://uri
    ${NS}    child3/grand-child-2/ggc
    ${NS}    child3/grand-child-2/ggc2    xmlns=default
    ${NS}    child3/grand-child-3
    ${NS}    another    xmlns=default2
    ${NS}    another/child
    ${NS}    back

Saved XML is semantically same as original
    Save XML    ${NS}    ${OUTPUT}
    Elements Should Be Equal    ${NS}    ${OUTPUT}
    ${etree1} =    Parse Xml    ${NS}    keep_clark_notation=yep
    ${etree2} =    Parse Xml    ${OUTPUT}    keep_clark_notation=yep
    Elements Should Be Equal    ${etree1}    ${etree2}

Saved XML has same namespaces as original
    Saved XML Should Equal File    ${NS}    ${NS}

Element To String with namespaces
    ${full} =    Element To String    ${NS}
    ${another} =    Element To String    ${NS}    xpath=another
    ${orig} =    Get File    ${NS}
    Should Be Equal    ${full}       ${{re.search('<test .*</test>', $orig, flags=re.DOTALL).group()}}
    Should Be Equal    ${another}    ${{re.search('<another .*</another>', $orig, flags=re.DOTALL).group()}}

Element without namepace inside element with namespace
    Save XML    ${NO NS IN NS}    ${OUTPUT}
    Elements Should Be Equal    ${NO NS IN NS}    ${OUTPUT}
    Saved XML Should Equal    ${NO NS IN NS}    ${NO NS IN NS}
    Element Text Should Be    ${NO NS IN NS}    .    xpath=no/yes/no

Attribute namespaces are not handled
    ${elem} =    Parse XML    ${ATTR NS}
    Test Attribute Namespace Parsing With lxml    ${elem}
