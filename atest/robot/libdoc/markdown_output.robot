*** Settings ***
Resource          libdoc_resource.robot

*** Test Cases ***
Markdown-format library is written as Markdown
    Run Libdoc    ${TESTDATADIR}/MarkdownLibrary.py ${OUT MARKDOWN}
    ${expected} =    Get File    ${TESTDATADIR}/MarkdownLibrary.txt
    ${actual} =    Get File    ${OUT MARKDOWN}
    Should Be Equal    ${actual}    ${expected}
    [Teardown]    Remove File    ${OUT MARKDOWN}

Non-Markdown-format library is written verbatim, not converted
    Run Libdoc    ${TESTDATADIR}/DocFormatHtml.py ${OUT MARKDOWN}
    ${actual} =    Get File    ${OUT MARKDOWN}
    Should Contain    ${actual}    *bold* or <b>bold</b> http://example.com
    [Teardown]    Remove File    ${OUT MARKDOWN}
