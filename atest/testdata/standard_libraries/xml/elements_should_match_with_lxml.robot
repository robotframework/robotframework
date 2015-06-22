*** Settings ***
Suite Setup       Set lxml availability to suite metadata
Test Template     Elements should not match
Library           XML    use_lxml=yes
Resource          xml_resource.robot

*** Test Cases ***
Elements should match
    [Template]    Match Elements
    <tag>content</tag>    <tag>c*</tag>
    <tag a="1" b="421"/>    <tag a="?" b="4*"/>
    <root>\n<tag>some\ntext</tag>tail text</root>    <root>\n<tag>some*</tag>tail??ex?</root>

Tail text is not checked with root element
    [Template]    NONE
    ${elem} =    Get Element    ${TEST}    another/child
    Elements should match    ${elem}    <child>nöŋ-* t??t</child>

Different tag names
    <tag/>   <täg/>    Different tag name: tag != täg

Different attributes
    <tag a="12"/>   <tag a="?"/>    Different value for attribute 'a': '12' does not match '?'
    <tag a="1" c="3"/>   <tag a="?" b="?"/>
    ...   Different attribute names: ['a', 'c'] != ['a', 'b']

Different texts
    <tag>some text</tag>   <tag>no match*</tag>  Different text: 'some text' does not match 'no match*'
    <tag></tag>   <tag>?*</tag>    Different text: '' does not match '?*'

Different tail texts
    <root><tag/>tail</root>   <root><tag/>wrong*</root>
    ...    Different tail text at 'root/tag': 'tail' does not match 'wrong*'
    <root><tag/></root>   <root><tag/>?</root>
    ...    Different tail text at 'root/tag': '' does not match '?'

Differences in children
    <root><tag/></root>    <root><different/></root>
    ...    Different tag name at 'root/tag': tag != different
    <a a="a"><b><c><d/></c></b></a>    <a a="a"><b><c><wrong/></c></b></a>
    ...    Different tag name at 'a/b/c/d': d != wrong
    <root><tag/></root>    <root><tag a="1"/></root>
    ...    Different attribute names at 'root/tag': [] != ['a']
    <a><b><c a="a" b="b"/></b></a>    <a><b><c a="?" b="ä*"></c></b></a>
    ...    Different value for attribute 'b' at 'a/b/c': 'b' does not match 'ä*'
    <root><tag/></root>    <root><tag>?</tag></root>
    ...    Different text at 'root/tag': '' does not match '?'
    <root><tag><c1/><c2/></tag></root>    <root><tag/></root>
    ...    Different number of child elements at 'root/tag': 2 != 0

Differences in children with same name
    <root><tag>x</tag><tag/></root>    <root><tag>??</tag><tag/></root>
    ...    Different text at 'root/tag': 'x' does not match '??'
    <root><tag/><tag>x</tag></root>    <root><tag/><tag>??</tag></root>
    ...    Different text at 'root/tag[2]': 'x' does not match '??'
    <a><b/><b><c/><c/><d/><c d='e'/></b></a>    <a><b/><b><c/><c/><d/><c d='e?'/></b></a>
    ...    Different value for attribute 'd' at 'a/b[2]/c[3]': 'e' does not match 'e?'

Differences in children with non-ASCII path
    <å><ä><ö/><ö>oikea</ö></ä></å>    <å><ä><ö/><ö>*väärä*</ö></ä></å>
    ...    Different text at 'å/ä/ö[2]': 'oikea' does not match '*väärä*'

Normalize whitespace
    [Template]    NONE
    Elements should match    <p>\n\tThis \ \ \ text\n<i>spaces \ has</i> also \ in\ttail!\n</p>
    ...   <p>*This*<i>spaces*</i>*!</p>    normalize_whitespace=false
    Elements should match    <p>\n\tThis \ \ \ text\n<i>spaces \ has</i> also \ in\ttail!\n</p>
    ...   <p>This *<i>spaces ???</i>*!</p>    normalize_whitespace=yes
    Elements should not match    <tag>\ntext\n</tag>    <tag>\t*wrong*\t</tag>
    ...   Different text: 'text' does not match '*wrong*'    normalize

Exclude children
    [Template]    Elements should match
    ${TEST}    <test name="*">\n${SPACE*4}\n${SPACE*4}</test>    exclude_children=yes
    ${TEST}    <test name="????"/>    exclude    normalize

*** Keywords ***
Match Elements
    [Arguments]    ${source}    ${match}
    Elements Should Match    ${source}    ${match}
    ${source}=    Parse XML    ${source}
    Elements Should Match    ${source}    ${match}

Elements should not match
    [Arguments]    ${source}    ${expected}    ${error}    ${normalize}=${FALSE}    ${exclude}=false
    Run Keyword and Expect Error    ${error}
    ...    Elements Should Match    ${source}    ${expected}
    ...    normalize_whitespace=${normalize}    exclude_children=${exclude}
