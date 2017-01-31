*** Settings ***
Suite Setup       Set lxml availability to suite metadata
Test Setup        Parse XML To Test Variable    ${NS}    \${ROOT}    keep_clark_notation=yes
Library           XML    use_lxml=yes
Resource          xml_resource.robot

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

Saved XML has same namespaces as original
    Saved XML Should Equal File    ${ROOT}    ${NS}
    [Teardown]    Remove Output File

Attribute namespaces
    ${elem} =    Parse XML    ${ATTR NS}    keep_clark_notation=yes
    Test Attribute Namespace Parsing With lxml    ${elem}
