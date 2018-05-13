*** Settings ***
Suite Setup       Run Tests With Tag Docs
Test Template     Tag doc should be correct in output
Resource          atest_resource.robot

*** Test Cases ***
Simple Tag Doc
    3    f1    Doc with spaces and _under_scores_

Specify Tag Doc With Pattern
    1    d1    Doc-for-many-tags

Tag Doc With Multiple Matches
    2    d_2    Doc-for-many-tags & More

Tag Doc With Formatting
    4    t1    http://some.url *bold*

Tag Doc For Combined Statistics
    0    DX    Doc-for-many-tags

*** Keywords ***
Run Tests With Tag Docs
    ${opts} =    Catenate
    ...    --tagdoc "f1:Doc with spaces and _under_scores_"
    ...    --tagdoc "t_1:http://some.url *bold*"
    ...    --tagdoc _d_?_:Doc-for-many-tags
    ...    --tagdoc D2:More
    ...    --tagstatcombine d*:DX
    Run Tests    ${opts}    misc/normal.robot

Tag doc should be correct in output
    [Arguments]    ${index}    ${tag}    ${doc}
    ${stats} =    Get Tag Stat Nodes
    Should Be Equal    ${stats[${index}].text}    ${tag}
    Should Be Equal    ${stats[${index}].attrib['doc']}    ${doc}
