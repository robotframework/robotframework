*** Settings ***
Resource       atest_resource.robot
Suite Setup    Run Tests    --log log.html --report report.html    output/testcase_metadata.robot

*** Test Cases ***
Test Case Metadata Is Available In Result Model
    Test Case Metadata Should Be Correct

Test Case Metadata Is Written To XML Output
    ${owner} =    Get Element    ${OUTFILE}    .//test[@name="Test With Metadata"]/meta[@name="Owner"]
    Should Be Equal    ${owner.text}    Team Robot
    ${ticket} =    Get Element    ${OUTFILE}    .//test[@name="Test With Metadata"]/meta[@name="Ticket"]
    Should Be Equal    ${ticket.text}    RF-9999
    ${html} =    Get Element    ${OUTFILE}    .//test[@name="Test With Metadata"]/meta[@name="Html"]
    Should Be Equal    ${html.text}    <b>value</b> & data
    Element Should Not Exist    ${OUTFILE}    xpath=.//test[@name="Test Without Metadata"]/meta

Test Case Metadata Is Preserved By Rebot
    Copy Previous Outfile
    Run Rebot    --log rebot-log.html --report NONE    ${OUTFILE COPY}
    Test Case Metadata Should Be Correct

Test Case Metadata Is Included In Log Model
    Run Tests    --log log.html --report NONE    output/testcase_metadata.robot
    File Should Contain    ${OUTDIR}/log.html    Team Robot
    File Should Contain    ${OUTDIR}/log.html    RF-9999
    File Should Contain    ${OUTDIR}/log.html    &lt;b&gt;value&lt;/b&gt; &amp; data

*** Keywords ***
Test Case Metadata Should Be Correct
    ${with metadata} =    Check Test Case    Test With Metadata
    Should Be Equal    ${with metadata.metadata['Owner']}    Team Robot
    Should Be Equal    ${with metadata.metadata['Ticket']}    RF-9999
    Should Be Equal    ${with metadata.metadata['Html']}    <b>value</b> & data
    ${without metadata} =    Check Test Case    Test Without Metadata
    Should Be Empty    ${without metadata.metadata}
