*** Settings ***
Resource       atest_resource.robot
Suite Setup    Run Tests    --log log.html --report report.html    parsing/test_metadata.robot    validate output=True

*** Test Cases ***
Metadata is available in modlel
    Validate metadata in model

Metadata is included in XML
    Validate metadata in XML

Metadata is included in log
    Validate metadate in HTML    ${OUTDIR}/log.html

Metadata is included in report
    Validate metadate in HTML    ${OUTDIR}/report.html

Metadata is preserved by Rebot
    Copy Previous Outfile
    Run Rebot    --log rebot-log.html --report NONE    ${OUTFILE COPY}
    Validate metadata in model

Metadata is included in JSON
    Copy Previous Outfile
    Run Tests    -o output.json    parsing/test_metadata.robot    output=${OUTDIR}/output.json    validate output=True
    Validate metadata in model
    Outputs Should Contain Same Data    ${OUTFILE COPY}    ${OUTDIR}/output.json    ignore_timestamps=True

*** Keywords ***
Validate metadata in model
    ${tc} =    Check Test Case    Test With Metadata
    Should Be Equal    ${tc.metadata}[Owner]     Team Robot
    Should Be Equal    ${tc.metadata}[Ticket]    RF-4409
    Should Be Equal    ${tc.metadata}[Escape]    not <b>bold</b> & <extra>
    Should Be Equal    ${tc.metadata}[Format]    *bold* & <extra>
    ${tc} =    Check Test Case    Test Without Metadata
    Should Be Empty    ${tc.metadata}

Validate metadata in XML
    ${tc} =    Get Element    ${OUTFILE}    xpath=.//test[@name="Test With Metadata"]
    Element Text Should Be    ${tc}    Team Robot                   xpath=meta[@name="Owner"]
    Element Text Should Be    ${tc}    RF-4409                      xpath=meta[@name="Ticket"]
    Element Text Should Be    ${tc}    not <b>bold</b> & <extra>    xpath=meta[@name="Escape"]
    Element Text Should Be    ${tc}    *bold* & <extra>             xpath=meta[@name="Format"]
    Element Should Not Exist    ${OUTFILE}    xpath=.//test[@name="Test Without Metadata"]/meta

Validate metadate in HTML
    [Arguments]    ${path}
    File Should Contain    ${path}    Team Robot
    File Should Contain    ${path}    RF-4409
    File Should Contain    ${path}    not &lt;b&gt;bold&lt;/b&gt; &amp; &lt;extra&gt;
    File Should Contain    ${path}    <b>bold\\x3c/b> &amp; &lt;extra&gt;
