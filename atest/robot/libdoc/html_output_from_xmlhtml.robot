*** Settings ***
Resource          libdoc_resource.robot
Suite Setup       Run Libdoc to XML:HTML and to HTML and Parse Models    ${TESTDATADIR}/module.py
Test Template     Should Be Equal As Strings

*** Keywords ***
Run Libdoc to XML:HTML and to HTML and Parse Models
    [Arguments]    ${library_path}
    Run Libdoc And Set Output    --format XML:HTML ${library_path} ${OUTXML}
    Run Libdoc And Parse Model From HTML    ${OUTXML}
    Set Suite Variable    ${XML-MODEL}    ${MODEL}
    Run Libdoc And Parse Model From HTML    ${library_path}

*** Comments ***
This test suite will be changed with one of the next Tasks to contain a check for the roundtrip from library into XML then from XML to html.
*** Test Cases ***
Name
    ${XML-MODEL}[name]    ${MODEL}[name]

Documentation
    ${XML-MODEL}[doc]    ${MODEL}[doc]

Version
    ${XML-MODEL}[version]    ${MODEL}[version]

Scope
    ${XML-MODEL}[scope]    ${MODEL}[scope]

Named Args
    ${XML-MODEL}[named_args]    ${MODEL}[named_args]

Inits
    ${XML-MODEL}[inits]    ${MODEL}[inits]

Keyword Names
    ${XML-MODEL}[keywords][0][name]    ${MODEL}[keywords][0][name]
    ${XML-MODEL}[keywords][1][name]    ${MODEL}[keywords][1][name]
    ${XML-MODEL}[keywords][13][name]    ${MODEL}[keywords][13][name]

Keyword Arguments
    ${XML-MODEL}[keywords][0][args]    ${MODEL}[keywords][0][args]
    ${XML-MODEL}[keywords][1][args]    ${MODEL}[keywords][1][args]
    ${XML-MODEL}[keywords][6][args]    ${MODEL}[keywords][6][args]
    ${XML-MODEL}[keywords][10][args]    ${MODEL}[keywords][10][args]
    ${XML-MODEL}[keywords][12][args]    ${MODEL}[keywords][12][args]
    ${XML-MODEL}[keywords][13][args]    ${MODEL}[keywords][13][args]

Embedded Arguments
    ${XML-MODEL}[keywords][14][name]    ${MODEL}[keywords][14][name]
    ${XML-MODEL}[keywords][14][args]    ${MODEL}[keywords][14][args]

Keyword Documentation
    ${XML-MODEL}[keywords][1][doc]    ${MODEL}[keywords][1][doc]
    ${XML-MODEL}[keywords][0][doc]    ${MODEL}[keywords][0][doc]
    ${XML-MODEL}[keywords][5][doc]    ${MODEL}[keywords][5][doc]
    ${XML-MODEL}[keywords][8][doc]    ${MODEL}[keywords][8][doc]
    ${XML-MODEL}[keywords][11][doc]    ${MODEL}[keywords][11][doc]

Keyword Short Doc
    ${XML-MODEL}[keywords][1][shortdoc]    ${MODEL}[keywords][1][shortdoc]
    ${XML-MODEL}[keywords][0][shortdoc]    ${MODEL}[keywords][0][shortdoc]
    ${XML-MODEL}[keywords][8][shortdoc]    ${MODEL}[keywords][8][shortdoc]
    ${XML-MODEL}[keywords][11][shortdoc]    ${MODEL}[keywords][11][shortdoc]
    ${XML-MODEL}[keywords][5][shortdoc]    ${MODEL}[keywords][5][shortdoc]

Keyword tags
    ${XML-MODEL}[keywords][1][tags]    ${MODEL}[keywords][1][tags]
    ${XML-MODEL}[keywords][2][tags]    ${MODEL}[keywords][2][tags]
    ${XML-MODEL}[keywords][3][tags]    ${MODEL}[keywords][3][tags]
    ${XML-MODEL}[keywords][4][tags]    ${MODEL}[keywords][4][tags]

TOC doc
    [Template]    None
    Run Libdoc to XML:HTML and to HTML and Parse Models    ${TESTDATADIR}/TOCWithInitsAndKeywords.py
    Should Be Equal As Strings    ${XML-MODEL}[doc]    ${MODEL}[doc]
