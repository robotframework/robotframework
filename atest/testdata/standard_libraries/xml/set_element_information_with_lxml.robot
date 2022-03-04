*** Settings ***
Suite Setup       Set lxml availability to suite metadata
Test Setup        Parse XML To Test Variable    ${SIMPLE}    \${XML}
Library           XML    use_lxml=yes
Resource          xml_resource.robot

*** Test Cases ***
Set Element Tag
    Set Element Tag    ${XML}    kekkonen
    Should Be Equal    ${XML.tag}    kekkonen

Set Element Tag Using Xpath
    Set Element Tag    ${XML}    kekkonen    xpath=child
    Should Be Equal    ${XML.tag}    root
    Element Text Should Be    ${XML}    text    xpath=kekkonen

Set Element Tag Returns Root Element
    ${root} =    Set Element Tag    ${SIMPLE}    new
    Should Be Equal    ${root.tag}    new
    ${root} =    Set Element Tag    ${SIMPLE}    new    xpath=c2/gc
    Should Be Equal    ${root.tag}    root
    Element Should Exist    ${root}    c2/new

Set Elements Tag
    [Setup]    Parse XML To Test Variable    ${TEST}    \${XML}
    Set Elements Tag    ${XML}    new    xpath=child
    @{texts} =    Get Elements Texts    ${XML}    xpath=new    normalize_whitespace=yes
    ${texts} =    Catenate    SEPARATOR=::    @{texts}
    Should Be Equal    ${texts}   child 1 text::child 2 text grand child text more text::
    Set Elements Tag    ${XML}    new    xpath=non-existing

Set Elements Tag returns root element
    ${root} =    Set Elements Tag    ${SIMPLE}    new
    Should Be Equal    ${root.tag}    new
    ${root} =    Set Elements Tag    ${SIMPLE}    new    xpath=child
    Should Be Equal    ${root.tag}       root
    Should Be Equal    ${root[0].tag}    new

Set Element Text
    Set Element Text    ${XML}    new    xpath=child
    Element Text Should Be    ${XML}    new    xpath=child

Set Element Text And Tail
    ${child} =    Get Element    ${XML}    child
    Set Element Text    ${XML}    new text    new tail    xpath=child
    Should Be Equal    ${child.text}    new text
    Should Be Equal    ${child.tail}    new tail
    Set Element Text    ${child}    tail=
    Should Be Equal    ${child.text}    new text
    Should Be Equal    ${child.tail}    ${EMPTY}
    Set Element Text    ${child}    text=final value
    Should Be Equal    ${child.text}    final value
    Should Be Equal    ${child.tail}    ${EMPTY}

Set Element Text Returns Root Element
    ${root} =    Set Element Text    ${SIMPLE}    new    xpath=child
    Should Be Equal    ${root.text}    ${NONE}
    Element Text Should Be    ${root}    new    xpath=child

Set Elements Text
    [Setup]    Parse XML To Test Variable    ${TEST}    \${XML}
    Set Elements Text    ${XML}    new text    ${SPACE}new tail   xpath=child/grandchild
    @{texts} =    Get Elements Texts    ${XML}    xpath=child    normalize_whitespace=yes
    ${texts} =    Catenate    SEPARATOR=::    @{texts}
    Should Be Equal    ${texts}   child 1 text::child 2 text new text new tail::new text new tail
    Set Elements Text    ${XML}    new text    xpath=non-existing

Set Elements Text Returns Root Element
    ${root} =    Set Elements Text    ${SIMPLE}    new    xpath=child
    Should Be Equal    ${root.text}    ${NONE}
    Element Text Should Be    ${root}    new    xpath=child

Set Element Attribute
    Set Element Attribute    ${XML}    attr    value
    Element Attribute Should Be    ${XML}    attr    value

Set element Attribute should fail with empty name
    [Documentation]    FAIL    Attribute name can not be empty.
    Set Element Attribute    ${XML}    ${EMPTY}    value

Overwrite Element Attribute
    Set Element Attribute    ${XML}    id    new    xpath=child
    Element Attribute Should Be    ${XML}    id    new    xpath=child

Set Element Attribute Returns Root Element
    ${root} =    Set Element Attribute    ${SIMPLE}    new    value    xpath=c2
    Should Be Empty    ${root.attrib}
    Element Attribute Should Be    ${root}    new    value    xpath=c2

Set Elements Attribute
    [Setup]    Parse XML To Test Variable    ${TEST}    \${XML}
    Set Elements Attribute    ${XML}    a2    new value   xpath=child
    ${elements} =    Get Elements    ${XML}    xpath=child
    Element Attribute Should Be    ${elements[0]}    a2    new value
    Element Attribute Should Be    ${elements[1]}    a2    new value
    Element Attribute Should Be    ${elements[2]}    a2    new value
    Set Elements Attribute    ${XML}    a2    new value   xpath=non-existing

Set Elements Attribute Returns Root Element
    ${root} =    Set Elements Attribute    ${SIMPLE}    new    value    xpath=c2
    Should Be Empty    ${root.attrib}
    Element Attribute Should Be    ${root}    new    value    xpath=c2

Remove Element Attribute
    Remove Element Attribute    ${XML}    id    xpath=child
    Element Attribute Should Be    ${XML}    id    ${NONE}    xpath=child

Removing Non-Existing Attribute Passes
    Remove Element Attribute    ${XML}    nonex
    Should Be Empty    ${XML.attrib}

Remove Element Attribute Returns Root Element
    ${root} =    Remove Element Attribute    ${SIMPLE}    id    xpath=child
    Element Attribute Should Be    ${root}    id    ${NONE}    xpath=child

Remove Elements Attribute
    [Setup]    Parse XML To Test Variable    ${TEST}    \${XML}
    Remove Elements Attribute    ${XML}    id    xpath=child
    ${elements} =    Get Elements    ${XML}    xpath=child
    Element Should Not Have Attribute    ${elements[0]}    id
    Element Should Not Have Attribute    ${elements[1]}    id
    Element Should Not Have Attribute    ${elements[2]}    id
    Remove Elements Attribute    ${XML}    id    xpath=non-existing

Remove Elements Attribute Returns Root Element
    ${root} =    Remove Elements Attribute    ${SIMPLE}    id    xpath=child
    Element Attribute Should Be    ${root}    id    ${NONE}    xpath=child

Remove Element Attributes
    Remove Element Attributes    ${XML}
    Should Be Empty    ${XML.attrib}
    Remove Element Attributes    ${XML}    xpath=child
    ${attrib} =    Get Element Attributes    ${XML}    xpath=child
    Should Be Empty    ${attrib}

Remove Element Attributes Returns Root Element
    ${root} =    Remove Element Attributes    ${SIMPLE}    xpath=child
    Element Attribute Should Be    ${root}    id    ${NONE}    xpath=child

Remove Elements Attributes
    [Setup]    Parse XML To Test Variable    ${TEST}    \${XML}
    Remove Elements Attributes    ${XML}    xpath=child
    ${elements} =    Get Elements    ${XML}    xpath=child
    Should Be Empty    ${elements[0].attrib}
    Should Be Empty    ${elements[1].attrib}
    Should Be Empty    ${elements[2].attrib}
    Remove Elements Attributes    ${XML}    xpath=non-existing

Remove Elements Attributes Returns Root Element
    ${root} =    Remove Elements Attributes    ${SIMPLE}    xpath=child
    Element Attribute Should Be    ${root}    id    ${NONE}    xpath=child
