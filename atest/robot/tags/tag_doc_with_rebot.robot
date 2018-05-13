*** Settings ***
Suite Setup       Run Tests And Rebot With Tag Doc
Resource          atest_resource.robot
Test Template     Tag doc should be correct in output

*** Test Cases ***
Simple Tag Doc
    3    f1    Doc for Rebot with spaces and _under_scores_

Specify Tag Doc With Pattern
    1    d1    Doc-for-many-rebot-tags

Tag Doc With Multiple Matches
    2    d_2    Doc-for-many-rebot-tags & More

Tag Doc With Formatting
    4    t1    http://some.url *bold*

Tag Doc For Combined Statistics
    0    DX    Doc-for-many-rebot-tags


*** Keywords ***

Run Tests And Rebot With Tag Doc
    Run Tests Without Processing Output    ${EMPTY}    misc/normal.robot
    ${opts} =    Catenate
    ...    --tagdoc "f1:Doc for Rebot with spaces and _under_scores_"
    ...    --tagdoc "t_1:http://some.url *bold*"
    ...    --tagdoc _d_?_:Doc-for-many-rebot-tags
    ...    --tagdoc D2:More
    ...    --tagstatcombine d*:DX
    Copy Previous Outfile
    Run Rebot    ${opts}    ${OUTFILE COPY}

Tag doc should be correct in output
    [Arguments]    ${index}    ${tag}    ${doc}
    ${stats} =    Get Tag Stat Nodes
    Should Be Equal    ${stats[${index}].text}    ${tag}
    Should Be Equal    ${stats[${index}].attrib['doc']}    ${doc}

