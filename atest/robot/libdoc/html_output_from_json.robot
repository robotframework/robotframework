*** Settings ***
Resource          libdoc_resource.robot
Suite Setup       Run Libdoc to JSON and to HTML and Parse Models    ${TESTDATADIR}/module.py
Test Template     Should Be Equal As Strings

*** Test Cases ***
Name
    ${JSON-MODEL}[name]    ${MODEL}[name]

Documentation
    ${JSON-MODEL}[doc]    ${MODEL}[doc]

Version
    ${JSON-MODEL}[version]    ${MODEL}[version]

Scope
    ${JSON-MODEL}[scope]    ${MODEL}[scope]

Inits
    ${JSON-MODEL}[inits]    ${MODEL}[inits]

Keyword Names
    ${JSON-MODEL}[keywords][0][name]    ${MODEL}[keywords][0][name]
    ${JSON-MODEL}[keywords][1][name]    ${MODEL}[keywords][1][name]
    ${JSON-MODEL}[keywords][11][name]    ${MODEL}[keywords][11][name]

Keyword Arguments
    [Template]    List of Dict Should Be Equal
    ${JSON-MODEL}[keywords][0][args]    ${MODEL}[keywords][0][args]
    ${JSON-MODEL}[keywords][1][args]    ${MODEL}[keywords][1][args]
    ${JSON-MODEL}[keywords][6][args]    ${MODEL}[keywords][6][args]
    ${JSON-MODEL}[keywords][9][args]    ${MODEL}[keywords][9][args]
    ${JSON-MODEL}[keywords][10][args]    ${MODEL}[keywords][10][args]
    ${JSON-MODEL}[keywords][11][args]    ${MODEL}[keywords][11][args]
    ${JSON-MODEL}[keywords][12][args]    ${MODEL}[keywords][12][args]

Embedded Arguments names
    ${JSON-MODEL}[keywords][13][name]    ${MODEL}[keywords][13][name]

Embedded Arguments arguments
    [Template]    List of Dict Should Be Equal
    ${JSON-MODEL}[keywords][13][args]    ${MODEL}[keywords][13][args]

Keyword Documentation
    ${JSON-MODEL}[keywords][0][doc]    ${MODEL}[keywords][0][doc]
    ${JSON-MODEL}[keywords][1][doc]    ${MODEL}[keywords][1][doc]
    ${JSON-MODEL}[keywords][5][doc]    ${MODEL}[keywords][5][doc]
    ${JSON-MODEL}[keywords][7][doc]    ${MODEL}[keywords][7][doc]
    ${JSON-MODEL}[keywords][8][doc]    ${MODEL}[keywords][8][doc]

Keyword Short Doc
    ${JSON-MODEL}[keywords][0][shortdoc]    ${MODEL}[keywords][0][shortdoc]
    ${JSON-MODEL}[keywords][1][shortdoc]    ${MODEL}[keywords][1][shortdoc]
    ${JSON-MODEL}[keywords][7][shortdoc]    ${MODEL}[keywords][7][shortdoc]
    ${JSON-MODEL}[keywords][8][shortdoc]    ${MODEL}[keywords][8][shortdoc]

Keyword tags
    ${JSON-MODEL}[keywords][1][tags]    ${MODEL}[keywords][1][tags]
    ${JSON-MODEL}[keywords][2][tags]    ${MODEL}[keywords][2][tags]
    ${JSON-MODEL}[keywords][3][tags]    ${MODEL}[keywords][3][tags]
    ${JSON-MODEL}[keywords][4][tags]    ${MODEL}[keywords][4][tags]

TOC doc
    [Template]    None
    Run Libdoc to JSON and to HTML and Parse Models    ${TESTDATADIR}/TOCWithInitsAndKeywords.py
    Should Be Equal As Strings    ${JSON-MODEL}[doc]    ${MODEL}[doc]

*** Keywords ***
Run Libdoc to JSON and to HTML and Parse Models
    [Arguments]    ${library_path}
    Run Libdoc And Set Output    ${library_path} ${OUTJSON}
    Run Libdoc And Parse Model From HTML    ${OUTJSON}
    Set Suite Variable    ${JSON-MODEL}    ${MODEL}
    Run Libdoc And Parse Model From HTML    ${library_path}
