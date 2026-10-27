*** Settings ***
Resource         libdoc_resource.robot
Test Setup       Remove Output Files
Test Template    Test Format in HTML

*** Variables ***
${EXAMPLE LINK}    <a href="http://example.com">http://example.com</a>
${RAW DOC}         *bold* or <b>bold</b> http://example.com
${HTML DOC}        <b>bold</b> or &lt;b&gt;bold&lt;/b&gt; ${EXAMPLE LINK}
${MD DOC}          <p><em>bold</em> or <b>bold</b> ${EXAMPLE LINK}</p>
${INXML}           ${OUTBASE}-2.xml
${INJSON}          ${OUTBASE}-2.json

*** Test Cases ***
Robot format
    ${HTML DOC}    --docformat Robot

Text format
    *bold* or &lt;b&gt;bold&lt;/b&gt; ${EXAMPLE LINK}    --DocFormat TEXT

HTML format
    *bold* or <b>bold</b> http://example.com    -F html    shortdoc=*bold* or *bold* http://example.com

Markdown format
    [Template]    NONE
    [Tags]    require-markdown
    Test Format in HTML    ${MD DOC}
    ...    --docformat markdown
    ...    doc2=<p>Link to <code>Keyword</code> or not?</p>
    Should Contain    ${MODEL}[doc]
    ...    Here is <span class="sb">`code`</span>.
    Should Contain    ${MODEL}[keywords][2][doc]
    ...    This link to <a href="#Keyword" title="&quot;Keyword&quot; keyword">Keyword</a>
    Should Contain    ${MODEL}[keywords][2][doc]
    ...    <span class="gh">*** Test Cases ***</span>

reST format
    [Template]    NONE
    [Tags]    require-docutils    require-pygments
    Test Format in HTML    <em>bold</em> or &lt;b&gt;bold&lt;/b&gt; <a
    ...    --docformat rest
    ...    doc2=Link to <cite>Keyword</cite> or not?
    ...    int_link=<a class="reference external" href="https://docs.python.org/library/functions.html#int">int</a>
    Should Contain    ${MODEL}[keywords][3][doc]
    ...    This link to <a href="#Keyword" title="&quot;Keyword&quot; keyword" class="name">Keyword</a>
    Should Contain    ${MODEL}[keywords][3][doc]
    ...    <span class="gh">*** Test Cases ***</span>

Format from Python library
    *bold* or <b>bold</b> http://example.com    lib=DocFormatHtml.py    shortdoc=*bold* or *bold* http://example.com

Format from CLI overrides format from library
    ${HTML DOC}    -F robot    DocFormatHtml.py

XML/RAW output
    [Template]    Test Format in XML
    ${RAW DOC}    TEXT     -F TEXT          DocFormat.py
    ${RAW DOC}    ROBOT    --docfor RoBoT   DocFormatHtml.py
    ${RAW DOC}    HTML     ${EMPTY}         DocFormatHtml.py

JSON/RAW output
    [Template]    Test Format in JSON
    [Tags]    require-jsonschema
    ${RAW DOC}    TEXT     -F TEXT --specdocformat rAw    DocFormat.py
    ${RAW DOC}    ROBOT    --docfor RoBoT -s RAW          DocFormatHtml.py
    ${RAW DOC}    HTML     -s raw                         DocFormatHtml.py

XML/HTML output
    [Template]    Test Format in XML
    <p>${HTML DOC}</p>    HTML    --format xMl --specdocformat hTML    DocFormat.py
    <p>${HTML DOC}</p>    HTML    --format LiBSpec                     DocFormat.py
    <p>${HTML DOC}</p>    HTML    --docfor RoBoT -f XML -s HTML        DocFormatHtml.py
    <p>${HTML DOC}</p>    HTML    -F ROBOT --format xml -s html        DocFormat.py

JSON/HTML output
    [Template]    Test Format in JSON
    [Tags]    require-jsonschema
    <p>${HTML DOC}</p>    HTML    --format jSoN --specdocformat hTML    DocFormat.py
    <p>${HTML DOC}</p>    HTML    --format jSoN                         DocFormat.py
    <p>${HTML DOC}</p>    HTML    --docfor RoBoT -f JSON -s HTML        DocFormatHtml.py
    <p>${HTML DOC}</p>    HTML    -F ROBOT --format JSON -s html        DocFormat.py

XML/RAW input
    [Template]    NONE
    Test Format In XML     ${RAW DOC}     cli=-F ROBOT    format=ROBOT
    Copy File              ${OUTXML}      ${INXML}
    Test Format In XML     ${RAW DOC}     lib=${INXML}    format=ROBOT
    Test Format In HTML    ${HTML DOC}    lib=${INXML}

JSON/RAW input
    [Template]    NONE
    [Tags]    require-jsonschema
    Test Format In JSON    ${RAW DOC}            cli=-F Robot -s RAW    format=ROBOT
    Copy File              ${OUTJSON}            ${INJSON}
    Test Format In JSON    <p>${HTML DOC}</p>    lib=${INJSON}    format=HTML
    Test Format In HTML    ${HTML DOC}           lib=${INJSON}

XML/HTML input
    [Template]    NONE
    Test Format In XML     ${MD DOC}        cli=-F MARKDOWN --format XML -s HTML    format=HTML
    Copy File              ${OUTXML}        ${INXML}
    Test Format In XML     ${MD DOC}        lib=${INXML}    format=HTML
    Test Format In HTML    ${MD DOC}        lib=${INXML}    doc2=<p>Link to <code>Keyword</code> or not?</p>
    Should Contain         ${MODEL}[doc]    Here is <span class="sb">`code`</span>.

JSON/HTML input
    [Template]    NONE
    [Tags]    require-jsonschema
    Test Format In JSON    <p>${HTML DOC}</p>    cli=-F Robot     format=HTML
    Copy File              ${OUTJSON}            ${INJSON}
    Test Format In JSON    <p>${HTML DOC}</p>    lib=${INJSON}    format=HTML
    Test Format In HTML    ${HTML DOC}           lib=${INJSON}

*** Keywords ***
Test Format In HTML
    [Arguments]    ${doc}    ${cli}=    ${lib}=DocFormat.py
    ...    ${doc2}=Link to <a href="#Keyword" title="&quot;Keyword&quot; keyword" class="name">Keyword</a> or not?
    ...    ${shortdoc}=${RAWDOC}
    ...    ${int_link}=<a href="https://docs.python.org/library/functions.html#int">int</a>
    ${lib} =    Join Path    ${TESTDATADIR}    ${lib}
    Run Libdoc And Parse Model From HTML    ${cli} ${lib}
    Should Contain     ${MODEL}[doc]                      ${doc}
    Should Contain     ${MODEL}[keywords][0][doc]         ${doc}
    Should Contain     ${MODEL}[keywords][1][doc]         ${doc2}
    Should Be Equal    ${MODEL}[keywords][0][shortdoc]    ${shortdoc}
    Should Contain     ${MODEL}[typedocs][0][doc]         ${int_link}
    Should Contain     ${MODEL}[typedocs][1][doc]         ${doc}

Test Format In XML
    [Arguments]    ${expected}    ${format}    ${cli}=    ${lib}=DocFormat.py
    ${lib} =    Join Path    ${TESTDATADIR}    ${lib}
    Run Libdoc And Parse Output     ${cli} ${lib}
    Format Should Be    ${format}
    Keyword Doc Should Be    0    ${expected}

Test Format In JSON
    [Arguments]    ${expected}   ${format}    ${cli}=    ${lib}=DocFormat.py
    ${lib} =    Join Path    ${TESTDATADIR}    ${lib}
    Run Libdoc And Parse Model From JSON     ${cli} ${lib}
    Should Be Equal    ${MODEL}[docFormat]           ${format}
    Should Be Equal    ${MODEL}[keywords][0][doc]    ${expected}
