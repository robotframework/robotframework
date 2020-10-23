*** Settings ***
Resource         libdoc_resource.robot
Test Setup       Remove Output Files
Test Template    Test Format in HTML

*** Variables ***
${EXAMPLE URL}     http://example.com
${EXAMPLE LINK}    <a href="${EXAMPLE URL}">${EXAMPLE URL}</a>

*** Test Cases ***
Robot format
    <b>bold</b> or &lt;b&gt;bold&lt;/b&gt; ${EXAMPLE LINK}    --docformat Robot

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
    <b>bold</b> or &lt;b&gt;bold&lt;/b&gt; ${EXAMPLE LINK}    -F robot    DocFormatHtml.py

Format from Java library
    [Tags]    require-jython    require-tools.jar
    *bold* or <b>bold</b> ${EXAMPLE URL}                      ${EMPTY}    DocFormatHtml.java
    <b>bold</b> or &lt;b&gt;bold&lt;/b&gt; ${EXAMPLE LINK}    -F robot    DocFormatHtml.java

Format in XML
    [Template]    Test Format in XML
    TEXT     -F TEXT          DocFormat.py
    ROBOT    --docfor RoBoT   DocFormatHtml.py
    HTML     ${EMPTY}         DocFormatHtml.py

Format in LIBSPEC
    [Template]    Test Format in LIBSPEC
    --format xMl --specdocformat hTML            DocFormat.py
    --docfor RoBoT -f XML -s HTML   DocFormatHtml.py
    -F ROBOT --format xml -s html   DocFormat.py

Format from XML spec
    [Template]    NONE
    Run Libdoc    -F HTML ${TESTDATADIR}/DocFormat.py ${OUTXML}
    Copy File    ${OUTXML}    ${OUTBASE}-2.xml
    Test Format In XML    HTML    lib=${OUTBASE}-2.xml

Format from LIBSPEC spec
    [Template]    NONE
    Run Libdoc    -F ROBOT --format XML -s HTML ${TESTDATADIR}/DocFormat.py ${OUTXML}
    Copy File    ${OUTXML}    ${OUTBASE}-2.xml
    Test Format In LIBSPEC    lib=${OUTBASE}-2.xml

Compare HTML from LIBSPEC
    [Template]    NONE
    Run Libdoc    -F ROBOT --format XML -s HTML ${TESTDATADIR}/DocFormat.py ${OUTXML}
    Test Format In HTML    <b>bold</b> or &lt;b&gt;bold&lt;/b&gt; ${EXAMPLE LINK}
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
    [Arguments]    ${format}    ${cli}=    ${lib}=DocFormat.py
    ${lib} =    Join Path    ${TESTDATADIR}    ${lib}
    Run Libdoc And Parse Output     ${cli} ${lib}
    Format should be    ${format}
    Keyword Doc Should Be    0    *bold* or <b>bold</b> http://example.com

Test Format In LIBSPEC
    [Arguments]    ${cli}=    ${lib}=DocFormat.py
    ${lib} =    Join Path    ${TESTDATADIR}    ${lib}
    Run Libdoc And Parse Output     ${cli} ${lib}
    Format should be    HTML
    Keyword Doc Should Be    0    <p><b>bold</b> or &lt;b&gt;bold&lt;/b&gt; ${EXAMPLE LINK}</p>
