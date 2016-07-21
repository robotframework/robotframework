*** Settings ***
Suite Setup     Run Tests And Rebot With Tag Doc
Resource        atest_resource.robot
Test Template   Tag doc should be correct in output


*** Test Cases ***

Simple Tag Doc
    3    f1    Some documentation for rebot

Specify Tag Doc With Pattern
    1    d1    Doc for many rebot tags

Tag Doc With Multiple Matches
    2    d_2    Doc for many rebot tags & More doc

Tag Doc With Formatting
    4    t1    http://some.url *bold*

Tag Doc For Combined Statistics
    0    DX    Doc for many rebot tags


*** Keywords ***

Run Tests And Rebot With Tag Doc
    Run Tests Without Processing Output  ${EMPTY}  misc/normal.robot
    ${opts} =  Catenate
    ...  --tagdoc f1:Some_documentation_for_rebot
    ...  --tagdoc t_1:http://some.url_*bold*
    ...  --tagdoc _d_?_:Doc_for_many_rebot_tags
    ...  --tagdoc D2:More_doc
    ...  --tagstatcombine d*:DX
    Copy Previous Outfile
    Run Rebot  ${opts}  ${OUTFILE COPY}

Tag doc should be correct in output
    [Arguments]  ${index}  ${tag}  ${doc}
    ${stats} =  Get Tag Stat Nodes
    Should Be Equal  ${stats[${index}].text}  ${tag}
    Should Be Equal  ${stats[${index}].attrib['doc']}  ${doc}

