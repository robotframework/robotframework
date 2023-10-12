*** Settings ***
Library           XML
Resource          xml_resource.robot
Test Setup        Parse XML To Test Variable    ${NS}    \${ROOT}    keep_clark_notation=yeah!

*** Test Cases ***
Tag names contain namespace in Clark Notation
    Should Be Equal    ${ROOT.tag}    {default}test
    ${children} =    Get Child Elements    ${ROOT}
    Should Be Equal    ${children[0].tag}    {default}child1
    Should Be Equal    ${children[1].tag}    {http://uri}child2
    Should Be Equal    ${children[2].tag}    {whatever.xsd}child3
    Should Be Equal    ${children[3].tag}    {default2}another
    Should Be Equal    ${children[4].tag}    {default}back

Clarck Notation must be used in xpaths
    [Template]    Element Text Should Be
    ${ROOT}    default ns        xpath={default}child1
    ${ROOT}    ns with prefix    xpath={http://uri}child2
    ${ROOT}    2nd prefix        xpath={whatever.xsd}child3/{whatever.xsd}grand-child
    ${ROOT}    1st prefix again  xpath={whatever.xsd}child3/{http://uri}grand-child-2/{http://uri}ggc
    ${ROOT}    default ns 2      xpath={whatever.xsd}child3/{http://uri}grand-child-2/{default}ggc2
    ${ROOT}    2nd default       xpath={default2}another/{default2}child
    ${ROOT}    back in default   xpath={default}back

xmlns attributes are removed
    [Template]    Element Should Have Attributes
    ${ROOT}    .    name=root
    ${ROOT}    {default}child1    id=1
    ${ROOT}    {http://uri}child2
    ${ROOT}    {whatever.xsd}child3
    ${ROOT}    {whatever.xsd}child3/{whatever.xsd}grand-child
    ${ROOT}    {whatever.xsd}child3/{http://uri}grand-child-2
    ${ROOT}    {whatever.xsd}child3/{http://uri}grand-child-2/{http://uri}ggc
    ${ROOT}    {whatever.xsd}child3/{http://uri}grand-child-2/{default}ggc2
    ${ROOT}    {whatever.xsd}child3/{whatever.xsd}grand-child-3
    ${ROOT}    {default2}another
    ${ROOT}    {default2}another/{default2}child
    ${ROOT}    {default}back

Parsed XML is semantically same as original
    Save XML    ${ROOT}    ${OUTPUT}
    ${root2} =    Parse XML    ${OUTPUT}    keep_clark_notation=yes please
    Elements Should Be Equal    ${ROOT}    ${root2}
    [Teardown]    Remove Output File

Prefixes are mangled when XML is saved
    @{expected} =    Run Keyword Depending On Etree Version
    ...    Get Expected Etree 1.3 Output
    ...    Get Expected Etree 1.2 Output
    Saved XML Should Equal    ${ROOT}    @{expected}
    [Teardown]    Remove Output File

Attribute namespaces
    ${elem} =    Parse XML    ${ATTR NS}    keep_clark_notation=yes
    Test Attribute Namespace Parsing    ${elem}

*** Keywords ***
Get Expected Etree 1.3 Output
    @{expected} =    Create List
    ...    <ns0:test xmlns:ns0="default" xmlns:ns1="http://uri" xmlns:ns2="whatever.xsd" xmlns:ns3="default2" name="root">
    ...    ${INDENT}<ns0:child1 id="1">default ns</ns0:child1>
    ...    ${INDENT}<ns1:child2>ns with prefix</ns1:child2>
    ...    ${INDENT}<ns2:child3>
    ...    ${INDENT}${INDENT}<ns2:grand-child>2nd prefix</ns2:grand-child>
    ...    ${INDENT}${INDENT}<ns1:grand-child-2>
    ...    ${INDENT}${INDENT}${INDENT}<ns1:ggc>1st prefix again</ns1:ggc>
    ...    ${INDENT}${INDENT}${INDENT}<ns0:ggc2>default ns 2</ns0:ggc2>
    ...    ${INDENT}${INDENT}</ns1:grand-child-2>
    ...    ${INDENT}${INDENT}<ns2:grand-child-3>2nd prefix 2</ns2:grand-child-3>
    ...    ${INDENT}</ns2:child3>
    ...    ${INDENT}<ns3:another>
    ...    ${INDENT}${INDENT}<ns3:child>2nd default</ns3:child>
    ...    ${INDENT}</ns3:another>
    ...    ${INDENT}<ns0:back>back in default</ns0:back>
    ...    </ns0:test>
    RETURN    @{expected}

Get Expected Etree 1.2 Output
    @{expected} =    Create List
    ...    <ns0:test name="root" xmlns:ns0="default">
    ...    ${INDENT}<ns0:child1 id="1">default ns</ns0:child1>
    ...    ${INDENT}<ns1:child2 xmlns:ns1="http://uri">ns with prefix</ns1:child2>
    ...    ${INDENT}<ns1:child3 xmlns:ns1="whatever.xsd">
    ...    ${INDENT}${INDENT}<ns1:grand-child>2nd prefix</ns1:grand-child>
    ...    ${INDENT}${INDENT}<ns2:grand-child-2 xmlns:ns2="http://uri">
    ...    ${INDENT}${INDENT}${INDENT}<ns2:ggc>1st prefix again</ns2:ggc>
    ...    ${INDENT}${INDENT}${INDENT}<ns0:ggc2>default ns 2</ns0:ggc2>
    ...    ${INDENT}${INDENT}</ns2:grand-child-2>
    ...    ${INDENT}${INDENT}<ns1:grand-child-3>2nd prefix 2</ns1:grand-child-3>
    ...    ${INDENT}</ns1:child3>
    ...    ${INDENT}<ns1:another xmlns:ns1="default2">
    ...    ${INDENT}${INDENT}<ns1:child>2nd default</ns1:child>
    ...    ${INDENT}</ns1:another>
    ...    ${INDENT}<ns0:back>back in default</ns0:back>
    ...    </ns0:test>
    RETURN    @{expected}
