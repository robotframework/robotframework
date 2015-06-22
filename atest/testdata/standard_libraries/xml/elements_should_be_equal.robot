*** Settings ***
Library           XML
Resource          xml_resource.robot
Test Template     Elements should not be equal

*** Test Cases ***
Elements should be equal
    [Template]    Element should be equal to itself
    <tag/>
    <root><tag/></root>
    <tag a="1" b="2"/>
    <root>\n<tag>some\ntext</tag>tail text</root>

Tail text is not checked with root element
    [Template]    NONE
    ${elem} =    Get Element    ${TEST}    another/child
    Elements should be equal    ${elem}    <child>nöŋ-äŝĉíï tëxt</child>

Different tag names
    <tag/>   <täg/>    Different tag name: tag != täg

Different attributes
    <tag a="1"/>   <tag a="2"/>    Different value for attribute 'a': 1 != 2
    <tag a="1" c="3"/>   <tag b="1"/>
    ...   Different attribute names: ['a', 'c'] != ['b']

Different texts
    <tag>some text</tag>   <tag>different</tag>  Different text: some text != different
    <tag>some text</tag>   <tag/>    Different text: some text !=${SPACE}

Different tail texts
    <root><tag/>tail</root>   <root><tag/>wrong</root>
    ...    Different tail text at 'root/tag': tail != wrong
    <root><tag/>tail</root>   <root><tag/></root>
    ...    Different tail text at 'root/tag': tail !=${SPACE}

Different number of children
    <root><tag/><tag/></root>    <root><tag/></root>   Different number of child elements: 2 != 1

Differences in children
    <root><tag/></root>    <root><different/></root>
    ...    Different tag name at 'root/tag': tag != different
    <a a="a"><b><c><d/></c></b></a>    <a a="a"><b><c><wrong/></c></b></a>
    ...    Different tag name at 'a/b/c/d': d != wrong
    <root><tag/></root>    <root><tag a="1"/></root>
    ...    Different attribute names at 'root/tag': [] != ['a']
    <a><b><c a="a" b="b"/></b></a>    <a><b><c a="ä" b="b"></c></b></a>
    ...    Different value for attribute 'a' at 'a/b/c': a != ä
    <root><tag/></root>    <root><tag>text</tag></root>
    ...    Different text at 'root/tag': \ != text
    <root><tag><c1/><c2/></tag></root>    <root><tag/></root>
    ...    Different number of child elements at 'root/tag': 2 != 0

Differences in children with same name
    <root><tag>x</tag><tag/></root>    <root><tag>y</tag><tag/></root>
    ...    Different text at 'root/tag': x != y
    <root><tag/><tag>x</tag></root>    <root><tag/><tag>y</tag></root>
    ...    Different text at 'root/tag[2]': x != y
    <a><b/><b><c/><c/><d/><c/></b></a>    <a><b/><b><c/><c/><d/><c><e/></c></b></a>
    ...    Different number of child elements at 'a/b[2]/c[3]': 0 != 1

Differences in children with non-ASCII path
    <å><ä><ö/><ö>oikea</ö></ä></å>    <å><ä><ö/><ö>väärä</ö></ä></å>
    ...    Different text at 'å/ä/ö[2]': oikea != väärä

Normalize whitespace
    [Template]    NONE
    Elements should be equal    <p>Text with \ \ whitesapce\n.</p>    <p>Text with \ \ whitesapce\n.</p>
    ...    normalize_whitespace=false
    Elements should be equal    <p>\n\tThis \ \ \ text\n<i>spaces \ has</i> also \ in\ttail!\n</p>
    ...   <p>This text <i>spaces has</i> also in tail!</p>    ${FALSE}    normalize
    Elements should not be equal    <tag>\ntext \ here\n</tag>    <tag>\twrong \ here\t</tag>
    ...   Different text: text here != wrong here    normalize

Exclude children
    [Template]    Elements should be equal
    ${TEST}    <test name="root">\n${SPACE*4}\n${SPACE*4}</test>    exclude_children=yes
    ${TEST}    <test name="root"/>    exclude    normalize

*** Keywords ***
Element should be equal to itself
    [Arguments]    ${source}
    ${xml}=    Parse XML    ${source}
    Elements Should Be Equal    ${source}    ${xml}
    Elements Should Be Equal    ${xml}    ${source}

Elements should not be equal
    [Arguments]    ${source}    ${expected}    ${error}    ${normalize}=${FALSE}    ${exclude}=false
    Run Keyword and Expect Error    ${error}
    ...    Elements Should Be Equal    ${source}    ${expected}
    ...    normalize_whitespace=${normalize}    exclude_children=${exclude}
