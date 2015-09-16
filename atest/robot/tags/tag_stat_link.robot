*** Settings ***
Suite Setup     Run Tests With Tag Stat Links
Resource        atest_resource.robot
Test Template   Tag link should be correct in output


*** Test Cases ***

Tag Links Without Patterns
    6    t2    title:http://example.com

Tag Links With Pattern
    3    f1    Title:http://example.com/f
    5    t1    Title:http://example.com/t

Tag Links With Many Patterns
    4    sub3  sub title:s-b-s--3

Same Tag Matches Multiple Links
    1    d1    Title:http://example.com/d:::Title 1:http://1:::title:1:more:link

Link For Combined Tag
    0    DX    Title X:http://X


*** Keywords ***

Run Tests With Tag Stat Links
    ${opts} =  Catenate
    ...  --tagstatlink T2:http://example.com:title
    ...  --tagstatlink ?1:http://example.com/%1:Title
    ...  --TagStatL *?u?*:%2-%3-%2-%1-%4:%2u%3_title
    ...  --tagstatcombine d*:DX
    ...  --tagstatlink d?:http://%1:Title_%1
    ...  --TAGSTATLINK D1:1:more:link:title
    Run Tests  ${opts}  misc/suites

Tag link should be correct in output
    [Arguments]  ${index}  ${tag}  ${links}
    ${stats} =  Get Tag Stat Nodes
    Should Be Equal  ${stats[${index}].text}  ${tag}
    Should Be Equal  ${stats[${index}].attrib['links']}  ${links}
