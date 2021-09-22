*** Settings ***
Resource         libdoc_resource.robot
Test Setup       Remove Output Files
Test Template    Test Format in HTML

*** Variables ***
${EXAMPLE URL}     http://example.com
${EXAMPLE LINK}    <a href="${EXAMPLE URL}">${EXAMPLE URL}</a>
${RAW DOC}         *bold* or <b>bold</b> http://example.com
${HTML DOC}        <b>bold</b> or &lt;b&gt;bold&lt;/b&gt; ${EXAMPLE LINK}

*** Test Cases ***
Robot format
    ${HTML DOC}    --docformat Robot

Text format
    *bold* or &lt;b&gt;bold&lt;/b&gt; ${EXAMPLE LINK}    --DocFormat TEXT

HTML format
    *bold* or <b>bold</b> ${EXAMPLE URL}    -F html

reST format
    [Template]    NONE
    [Tags]    require-docutils    require-pygments
    Test Format in HTML    <em>bold</em> or &lt;b&gt;bold&lt;/b&gt; <a
    ...    --docformat rest    expected2=Link to <cite>Keyword</cite>.
    Should Contain    ${MODEL}[keywords][2][doc]
    ...    This link to <a href="#Keyword" class="name">Keyword</a>
    Should Contain    ${MODEL}[keywords][2][doc]
    ...    <span class=\"gh\">*** Test Cases ***\x3c/span>

Format from Python library
    *bold* or <b>bold</b> ${EXAMPLE URL}    lib=DocFormatHtml.py

Format from CLI overrides format from library
    ${HTML DOC}    -F robot    DocFormatHtml.py

Format in XML
    [Template]    Test Format in XML
    ${RAW DOC}    TEXT     -F TEXT          DocFormat.py
    ${RAW DOC}    ROBOT    --docfor RoBoT   DocFormatHtml.py
    ${RAW DOC}    HTML     ${EMPTY}         DocFormatHtml.py

Format in JSON RAW
    [Template]    Test Format in JSON
    ${RAW DOC}    TEXT     -F TEXT --specdocformat rAw    DocFormat.py
    ${RAW DOC}    ROBOT    --docfor RoBoT -s RAW          DocFormatHtml.py
    ${RAW DOC}    HTML     -s raw                         DocFormatHtml.py

Format in LIBSPEC
    [Template]    Test Format in XML
    <p>${HTML DOC}</p>    HTML    --format xMl --specdocformat hTML    DocFormat.py
    <p>${HTML DOC}</p>    HTML    --format LiBSpec                     DocFormat.py
    <p>${HTML DOC}</p>    HTML    --docfor RoBoT -f XML -s HTML        DocFormatHtml.py
    <p>${HTML DOC}</p>    HTML    -F ROBOT --format xml -s html        DocFormat.py

Format in JSON
    [Template]    Test Format in JSON
    <p>${HTML DOC}</p>    HTML    --format jSoN --specdocformat hTML    DocFormat.py
    <p>${HTML DOC}</p>    HTML    --format jSoN                         DocFormat.py
    <p>${HTML DOC}</p>    HTML    --docfor RoBoT -f JSON -s HTML        DocFormatHtml.py
    <p>${HTML DOC}</p>    HTML    -F ROBOT --format JSON -s html        DocFormat.py

Format from XML spec
    [Template]    NONE
    Test Format In XML    ${RAW DOC}    HTML    -F HTML    lib=DocFormat.py
    Copy File    ${OUTXML}    ${OUTBASE}-2.xml
    Test Format In XML    ${RAW DOC}    HTML    lib=${OUTBASE}-2.xml

Format from JSON RAW spec
    [Template]    NONE
    Test Format In JSON    ${RAW DOC}    ROBOT    -F Robot -s RAW    lib=DocFormat.py
    Copy File    ${OUTJSON}    ${OUTBASE}-2.json
    Test Format In JSON    <p>${HTML DOC}</p>    HTML    lib=${OUTBASE}-2.json

Format from LIBSPEC spec
    [Template]    NONE
    Test Format In XML    <p>${HTML DOC}</p>    HTML    -F ROBOT --format XML -s HTML    lib=DocFormat.py
    Copy File    ${OUTXML}    ${OUTBASE}-2.xml
    Test Format In XML    <p>${HTML DOC}</p>    HTML    lib=${OUTBASE}-2.xml

Format from JSON spec
    [Template]    NONE
    Test Format In JSON    <p>${HTML DOC}</p>    HTML    -F Robot    lib=DocFormat.py
    Copy File    ${OUTJSON}    ${OUTBASE}-2.json
    Test Format In JSON    <p>${HTML DOC}</p>    HTML    lib=${OUTBASE}-2.json

Compare HTML from LIBSPEC
    [Template]    NONE
    Run Libdoc    -F ROBOT --format XML -s HTML ${TESTDATADIR}/DocFormat.py ${OUTXML}
    Test Format In HTML    ${HTML DOC}
    ...                    lib=${OUTXML}

*** Keywords ***
Test Format In HTML
    [Arguments]    ${expected}    ${cli}=    ${lib}=DocFormat.py
    ...    ${expected2}=Link to <a href="#Keyword" class="name">Keyword</a>.
    ${lib} =    Join Path    ${TESTDATADIR}    ${lib}
    Run Libdoc And Parse Model From HTML    ${cli} ${lib}
    Should Contain    ${MODEL}[doc]                 ${expected}
    Should Contain    ${MODEL}[keywords][0][doc]    ${expected}
    Should Contain    ${MODEL}[keywords][1][doc]    ${expected2}

Test Format In XML
    [Arguments]    ${expected}    ${format}    ${cli}=    ${lib}=DocFormat.py
    ${lib} =    Join Path    ${TESTDATADIR}    ${lib}
    Run Libdoc And Parse Output     ${cli} ${lib}
    Format should be    ${format}
    Keyword Doc Should Be    0    ${expected}

Test Format In JSON
    [Arguments]    ${expected}   ${format}    ${cli}=    ${lib}=DocFormat.py
    ${lib} =    Join Path    ${TESTDATADIR}    ${lib}
    Run Libdoc And Parse Model From JSON     ${cli} ${lib}
    Should Be Equal    ${MODEL}[docFormat]    ${format}
    Should Be Equal    ${MODEL}[keywords][0][doc]    ${expected}
