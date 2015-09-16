*** Settings ***
Suite Setup     Run Tests With Tag Docs
Resource        atest_resource.robot
Test Template   Tag doc should be correct in output


*** Test Cases ***

Simple Tag Doc
    3    f1    Some documentation

Specify Tag Doc With Pattern
    1    d1    Doc for many tags

Tag Doc With Multiple Matches
    2    d_2    Doc for many tags & More doc

Tag Doc With Formatting
    4    t1    http://some.url *bold*

Tag Doc For Combined Statistics
    0    DX    Doc for many tags


*** Keywords ***

Run Tests With Tag Docs
    ${opts} =  Catenate
    ...  --tagdoc f1:Some_documentation
    ...  --tagdoc t_1:http://some.url_*bold*
    ...  --tagdoc _d_?_:Doc_for_many_tags
    ...  --tagdoc D2:More_doc
    ...  --tagstatcombine d*:DX
    Run Tests  ${opts}  misc/normal.robot

Tag doc should be correct in output
    [Arguments]  ${index}  ${tag}  ${doc}
    ${stats} =  Get Tag Stat Nodes
    Should Be Equal  ${stats[${index}].text}  ${tag}
    Should Be Equal  ${stats[${index}].attrib['doc']}  ${doc}
