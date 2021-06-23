*** Settings ***
Resource         libdoc_resource.robot
Suite Setup      Run Libdoc And Parse Model From HTML    ${TESTDATADIR}/InternalLinking.py
Test Template    Doc Should Contain Link

*** Test Cases ***
Linking to sections in introduction
    ${MODEL}    Introduction    Introduction
    ${MODEL}    Introduction    Library INTROduction
    ${MODEL}    Importing       importing
    ${MODEL}    Importing       Library Importing
    ${MODEL}    Keywords        Keywords

Linking to sections in importing and keywords
    ${MODEL['inits'][0]}       Introduction    introduction
    ${MODEL['keywords'][1]}    Importing       Importing

Linking to keywords in introduction
    ${MODEL}    Keyword           Keyword
    ${MODEL}    Second%20Keyword    secoNd kEywoRD

Linking to keywords in importing and keywords
    ${MODEL['inits'][0]}       Keyword           keyword
    ${MODEL['keywords'][1]}    Second%20Keyword    Second Keyword

Non-matching text in backticks gets formatting
    [Template]    Doc Should Contain Name
    ${MODEL}    backticks
    ${MODEL['keywords'][2]}    arg
    ${MODEL['keywords'][2]}    no link

Linking to first level headers in introduction
    [Template]    NONE
    Doc Should Contain Link    ${MODEL}    Linking%20to%20headers    linking to headers
    Doc Should Contain Link    ${MODEL}    First%20%3D%20Level%20%3D       first = level =
    Doc Should Contain    ${MODEL}    <h2 id="Linking to headers">Linking to headers</h2>
    Doc Should Contain    ${MODEL}    <h2 id="First = Level =">First = Level =</h2>

Linking to first level headers in importing and keywords
    ${MODEL['inits'][0]}       Formatting            formatting
    ${MODEL['keywords'][2]}    Linking%20to%20headers    linking to headers

Linking to second and third level headers
    [Template]    NONE
    Doc Should Contain Link    ${MODEL}                   Second%20level    Second level
    Doc Should Contain Link    ${MODEL}                   Third%20level     third level
    Doc Should Contain Link    ${MODEL['keywords'][2]}    Second%20level    Second LEVEL
    Doc Should Contain    ${MODEL}    <h3 id="Second level">Second level</h3>
    Doc Should Contain    ${MODEL}    <h4 id="Third level">Third level</h4>

Only headers in introduction are linkable
    [Template]    NONE
    Doc Should Contain Name    ${MODEL['keywords'][2]}    not linkable
    Doc Should Contain    ${MODEL['keywords'][2]}    <h2>Not linkable</h2>

Special characters are percent encoded
    ${MODEL['keywords'][0]}
    ...    Percent%20encoding%3A%20!%22%23%25%2F()%3D%3F%7C%2B-_.!~*'()
    ...    Percent encoding: !"#%/()=?|+-_.!~*'()

HTML entities are escaped also in name
    ${MODEL['keywords'][0]}
    ...    HTML%20entities%3A%20%26%3C%3E    HTML entities: &amp;&lt;&gt;

Non-ASCII is encoded
    ${MODEL['keywords'][0]}
    ...   Non-ASCII%3A%20%C3%A4%E2%98%83    Non-ASCII: ä\u2603

*** Keywords ***
Doc Should Contain Link
    [Arguments]    ${object}    ${target}    ${text}
    Doc Should Contain   ${object}    <a href="#${target}" class="name">${text}</a>

Doc Should Contain Name
    [Arguments]    ${object}    ${text}
    Doc Should Contain   ${object}    <span class="name">${text}</span>

Doc Should Contain
    [Arguments]    ${object}    ${text}
    Should Contain    ${object['doc']}    ${text}
