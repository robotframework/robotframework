*** Settings ***
Suite Setup       Set lxml availability to suite metadata
Library           XML    use_lxml=yes
Resource          xml_resource.robot

*** Test Cases ***
Get attribute of current element
    ${attr}=     Get Element Attribute    <tag a="1" b="2"/>    a
    Should Be Equal    ${attr}    1

Get attribute of child element
    ${attr}=     Get Element Attribute    <root><tag a="1"/></root>    a    tag
    Should Be Equal    ${attr}    1

Getting non-existing attribute returns None
    ${attr}=     Get Element Attribute    <tag a="1"/>    b
    Should Be Equal    ${attr}    ${None}

Default value is used when attribute does not exist
    ${attr}=     Get Element Attribute    <tag a="1"/>    b    default=value
    Should Be Equal    ${attr}    value
    ${attr}=     Get Element Attribute    <tag a="1"/>    a    default=value
    Should Be Equal    ${attr}    1

Get element attributes
    ${attrs}=   Get Element Attributes    <tag a="1" b="2"/>
    Should Be True    ${attrs} == {'a': '1', 'b': '2'}
    ${attrs}=   Get Element Attributes    <root><tag/></root>    tag
    Should Be Empty    ${attrs}

Modifying returned attributes does not affect original element
    ${elem}=    Parse XML    <tag a="1" b="2"/>
    ${attrs}=   Get Element Attributes    ${elem}
    Should Be True    ${attrs} == {'a': '1', 'b': '2'}
    Set To Dictionary    ${attrs}    c    3
    ${attrs}=   Get Element Attributes    ${elem}
    Should Be True    ${attrs} == {'a': '1', 'b': '2'}

Element attribute should be
    [Documentation]    FAIL 1 != 7
    Element Attribute Should Be    <tag a="1" b="2"/>    a    1
    Element Attribute Should Be    <root><tag a="1" b="2"/></root>    a    7    tag

Element attribute should be when no attribute exists
    [Documentation]    FAIL None != foo
    Element Attribute Should Be    <tag a="1" b="2"/>    c    ${None}
    Element Attribute Should Be    <tag a="1" b="2"/>    c    foo

Element attribute should be with custom error message
    [Documentation]    FAIL My message
    Element Attribute Should Be    <tag a="1"/>    a    x    message=My message

Element attribute should match
    [Documentation]    FAIL '1' does not match '??'
    Element Attribute Should Match    <tag a="foo-bar"/>    a    f*-???
    Element Attribute Should Match    <root><tag a="1"/></root>    a    ??    tag

Element attribute should match when no attribute exists
    [Documentation]    FAIL Attribute 'c' does not exist.
    Element Attribute Should Match    <tag a="1" b="2"/>    c    ${None}

Element attribute should match with custom error message
    [Documentation]    FAIL Special
    Element Attribute Should Match    <tag a="1"/>    a    ??    message=Special

Element should not have attribute
    [Documentation]    FAIL Attribute 'y' exists and has value '3'.
    Element Should Not Have Attribute    <elem/>    attr
    Element Should Not Have Attribute    <r x="1"><c y="2"/></r>    x    xpath=c
    Element Should Not Have Attribute    <r x="1"><c y="3"/></r>    y    xpath=c

Element should not have attribute with custom error message
    [Documentation]    FAIL Custom
    Element Should Not Have Attribute    <elem id="1"/>    id    message=Custom

Non-ASCII
    ${attr}=    Get Element Attribute    <täg ä='ö'/>    ä
    Should Be Equal    ${attr}    ö
    ${attrs}=    Get Element Attributes    <täg ä='ö'/>
    Should Be True    ${attrs} == {u'\\xe4': u'\\xf6'}
    Element Attribute Should Be    <täg ä='ö'/>    ä    ö
    Element Attribute Should Match    <täg ä='öö'/>    ä    ö?
