*** Settings ***
Library           XML
Resource          xml_resource.robot
Test Setup        Parse XML To Test Variable    ${SIMPLE}    \${XML}

*** Variables ***
${NEW}            <new attr="value"/>
${WITH TAIL}      <p>text with <b>bold</b>&amp;<i>italics</i>...</p>
${WITH TAIL 2}    <p><b>bold</b><i>italics</i>...</p>

*** Test Cases ***
Add Element
    ${elem} =    Parse XML    ${NEW}
    Add Element    ${XML}    ${elem}
    Element Attribute Should Be    ${XML}    attr    value    xpath=new
    ${children} =    Get Child Elements    ${XML}
    Should Be Equal    ${children[-1].tag}    new

Add Element As String
    Add Element    ${XML}    ${NEW}    xpath=c2
    Element Attribute Should Be    ${XML}    attr    value    xpath=c2/new

Add Element With Index
    Add Element    ${XML}    ${NEW}    index=0
    Element Attribute Should Be    ${XML}    attr    value    xpath=new
    ${children} =    Get Child Elements    ${XML}
    Should Be Equal    ${children[0].tag}    new

Added Element Is A Copy
    ${elem} =    Parse XML    ${NEW}
    Add Element    ${XML}    ${elem}
    Clear Element    ${elem}
    Element Attribute Should Be    ${XML}    attr    value    xpath=new

Add Element Returns Root Element
    ${root} =    Add Element    ${SIMPLE}    <new>element</new>    xpath=c2
    Element Text Should Be    ${root}    element    xpath=c2/new

Remove Element
    Remove Element    ${XML}    child
    Remove Element    ${XML}    xpath=c2
    Elements Should Be Equal    ${XML}    <root/>

Remove Non-Direct Child Element
    Remove Element    ${XML}    c2/gc
    Element Should Not Exist    ${XML}    c2/gc

Remove Element Keeps Tail By Default
    ${p} =    Remove Element    ${WITH TAIL}   i
    Elements Should Be Equal    ${p}    <p>text with <b>bold</b>&amp;...</p>
    Remove Element     ${p}    b
    Elements Should Be Equal    ${p}    <p>text with &amp;...</p>

Remove Element Keeps Tail When Parent or Sibling Contains No Text
    ${p} =    Remove Element    ${WITH TAIL2}   i
    Elements Should Be Equal    ${p}    <p><b>bold</b>...</p>
    Remove Element    ${p}    b    remove_tail=false
    Elements Should Be Equal    ${p}    <p>...</p>

Remove Element Can Be Configured To Remove Tail
    ${p} =    Remove Element    ${WITH TAIL}   i    remove_tail=True
    Elements Should Be Equal    ${p}    <p>text with <b>bold</b>&amp;</p>
    Remove Element     ${p}    b    remove_tail=YeS
    Elements Should Be Equal    ${p}    <p>text with </p>

Remove Element Fails If No Element Match
    [Documentation]    FAIL No element matching 'nonex' found.
    Remove Element    ${XML}    nonex

Remove Element Fails If Multiple Elements Match
    [Documentation]    FAIL Multiple elements (3) matching 'child' found.
    Remove Element    ${TEST}    child

Remove Element Requires Xpath
    [Documentation]    FAIL No xpath given.
    Remove Element    ${XML}

Remove Element Cannot Remove Root Element
    [Documentation]    FAIL Cannot remove root element.
    Remove Element    ${XML}    .

Remove Element Returns Root Element
    ${root} =    Remove Element    ${SIMPLE}    xpath=c2
    Element Should Not Exist    ${root}    xpath=c2

Remove Elements
    ${tree} =    Parse XML    ${TEST}
    Remove Elements    ${tree}    xpath=.//child
    Element Should Not Exist    ${tree}    .//child

Remove Elements Can Remove All Child Elements
    Remove Elements    ${XML}    *
    Elements Should Be Equal    ${XML}    <root/>

Remove Elements Does Not Fail If No Element Match
    Remove Elements    ${XML}    nonex

Remove Elements Keeps Tail By Default
    ${p} =    Remove Elements    ${WITH TAIL}    xpath=*
    Elements Should Be Equal    ${p}    <p>text with &amp;...</p>
    ${p} =    Remove Elements    ${WITH TAIL 2}    xpath=*    remove_tail=
    Elements Should Be Equal    ${p}    <p>...</p>

Remove Elements Can Be Configured To Remove Tail
    ${p} =    Remove Elements    ${WITH TAIL}    xpath=*    remove_tail=please
    Elements Should Be Equal    ${p}    <p>text with </p>

Remove Elements Requires Xpath
    [Documentation]    FAIL No xpath given.
    Remove Elements    ${XML}

Remove Elements Cannot Remove Root Element
    [Documentation]    FAIL Cannot remove root element.
    Remove Elements    ${XML}    .

Remove Elements Returns Root Element
    ${root} =    Remove Elements    ${SIMPLE}    xpath=c2
    Element Should Not Exist    ${root}    xpath=c2
