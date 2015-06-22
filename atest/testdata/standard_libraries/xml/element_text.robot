*** Settings ***
Library           XML
Resource          xml_resource.robot

*** Test Cases ***
Get text of current element
    ${text}=     Get Element Text    <tag>text</tag>
    Should Be Equal    ${text}    text

Get text of child element
    ${text}=     Get Element Text    <root><tag>text</tag></root>    tag
    Should Be Equal    ${text}    text

Get text of element with no text
    ${text}=     Get Element Text    <tag></tag>
    Should Be Equal    ${text}    ${EMPTY}
    ${text}=     Get Element Text    <tag/>
    Should Be Equal    ${text}    ${EMPTY}

Get text with whitespace
    ${text}=     Get Element Text    <tag>\nfoo \ bar\n</tag>
    Should Be Equal    ${text}     \nfoo \ bar\n
    ${text}=     Get Element Text    <tag>\nfoo \ bar\n</tag>    normalize_whitespace=False
    Should Be Equal    ${text}     \nfoo \ bar\n

Get text with whitespace normalized
    ${text}=     Get Element Text    <tag>\nfoo \ bar\n</tag>    .    normalize
    Should Be Equal    ${text}     foo bar

Get text of element containing children
    ${p}=    Catenate    SEPARATOR=\n
    ...    <p>
    ...    \ \ This <i>interesting "<b>example</b>"</i> spans \ \
    ...    \ \ \ \ <span id="x">multiple lines<i></i><i>...</i></span>
    ...    </p>
    ${text}=     Get Element Text    ${p}
    Should Be Equal    ${text}    \n${SPACE*2}This interesting "example" spans${SPACE*2}\n${SPACE*4}multiple lines...\n
    ${text}=     Get Element Text    ${p}    normalize_whitespace=True
    Should Be Equal    ${text}    This interesting "example" spans multiple lines...

Get texts of elements
    ${texts}=     Get Elements Texts    ${TEST}    child
    Length Should Be    ${texts}    3
    Should Be Equal    ${texts[0]}    child 1 text
    Should Be Equal    ${texts[1]}    \n${SPACE*8}child 2 text\n${SPACE*8}grand child text\n${SPACE*8}more text\n${SPACE*4}
    Should Be Equal    ${texts[2]}    ${EMPTY}

Get texts of elements whitespace normalized
    ${texts}=     Get Elements Texts    ${TEST}    child    normalize
    Length Should Be    ${texts}    3
    Should Be Equal    ${texts[0]}    child 1 text
    Should Be Equal    ${texts[1]}    child 2 text grand child text more text
    Should Be Equal    ${texts[2]}    ${EMPTY}

Element text should be
    [Documentation]    FAIL text != no dice
    Element Text Should Be    <tag>text</tag>    text
    Element Text Should Be    <root><tag>text</tag></root>    text    tag
    Element Text Should Be    <root><tag>text</tag></root>    no dice    tag

Element text should match
    [Documentation]    FAIL 'text' does not match 'no*'
    Element Text Should Match    <tag>text</tag>    te?t
    Element Text Should Match    <root><tag>text</tag></root>    t*    tag
    Element Text Should Match    <root><tag>text</tag></root>    no*    tag

Element text should be with whitespace normalized
    Element Text Should Be    <p>\n1 <i>2</i>\t<b>3</b>!\n</p>    1 2 3!
    ...    normalize_whitespace=yes
    Element Text Should Be    <r>1<tag>\n2\n3\n</tag>4</r>    2 3    tag    yes

Element text should match with whitespace normalized
    Element Text Should Match    <p>\n1 <i>2</i>\t<b>3</b>!\n</p>    1*!
    ...    normalize_whitespace=yes
    Element Text Should Match    <r>1<tag>\n2\n3\n</tag>4</r>    2?3    tag    yes

Element text should be failing with custom message
    [Documentation]    FAIL special
    Element Text Should Be    <tag>text</tag>    wrong    message=special

Element text should match failing with custom message
    [Documentation]    FAIL my message
    Element Text Should Match    <tag>text</tag>    x*x    message=my message

Non-ASCII
    ${text}=    Get Element Text    <p><i>hyvää</i> yötä</p>
    Should Be Equal    ${text}    hyvää yötä
    Element Text Should Be    <p><i>hyvää</i> yötä</p>    hyvää yötä
    Element Text Should Match    <p><i>hyvää</i> yötä</p>    ???ää yö*tä
