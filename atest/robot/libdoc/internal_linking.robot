*** Settings ***
Resource         libdoc_resource.robot
Suite Setup      Run Libdoc And Parse Model From HTML    ${TESTDATADIR}/InternalLinking.py
Test Template    Doc Should Contain Link

*** Test Cases ***
Linking to sections in introduction
    ${MODEL}
    ...    Introduction
    ...    Introduction
    ...    Introduction section
    ${MODEL}
    ...    Library INTROduction
    ...    Introduction
    ...    Introduction section
    ${MODEL}
    ...    importing
    ...    Importing
    ...    Importing section
    ${MODEL}
    ...    Library Importing
    ...    Importing
    ...    Importing section
    ${MODEL}
    ...    Keywords
    ...    Keywords
    ...    Keywords section

Linking to sections in importing and keywords
    ${MODEL}[inits][0]
    ...    introduction
    ...    Introduction
    ...    Introduction section
    ${MODEL}[keywords][1]
    ...    Importing
    ...    Importing
    ...    Importing section

Linking to keywords in introduction
    ${MODEL}
    ...    Keyword
    ...    Keyword
    ...    Keyword keyword
    ${MODEL}
    ...    secoNd kEywoRD
    ...    Second%20Keyword
    ...    Second Keyword keyword

Linking to keywords in importing and keywords
    ${MODEL}[inits][0]
    ...    keyword
    ...    Keyword
    ...    Keyword keyword
    ${MODEL}[keywords][1]
    ...    Second Keyword
    ...    Second%20Keyword
    ...    Second Keyword keyword

Linking to types
    ${MODEL}
    ...    str
    ...    type-string
    ...    string type
    ${MODEL}
    ...    float
    ...    type-float
    ...    float type

Non-matching text in backticks gets formatting
    [Template]    Doc Should Contain Name
    ${MODEL}                 backticks
    ${MODEL}[keywords][2]    arg
    ${MODEL}[keywords][2]    no link

Linking to first level headers in introduction
    [Template]    NONE
    Doc Should Contain Link    ${MODEL}
    ...    linking to headers
    ...    Linking%20to%20headers
    ...    Linking to headers section
    Doc Should Contain Link    ${MODEL}
    ...    first = level =
    ...    First%20%3D%20Level%20%3D
    ...    First = Level = section
    Doc Should Contain    ${MODEL}    <h2 id="Linking to headers">Linking to headers</h2>
    Doc Should Contain    ${MODEL}    <h2 id="First = Level =">First = Level =</h2>

Linking to first level headers in importing and keywords
    ${MODEL}[inits][0]
    ...    formatting
    ...    Formatting
    ...    Formatting section
    ${MODEL}[keywords][2]
    ...    linking to headers
    ...    Linking%20to%20headers
    ...    Linking to headers section

Linking to second and third level headers
    [Template]    NONE
    Doc Should Contain Link    ${MODEL}
    ...    Second level
    ...    Second%20level
    ...    Second level section
    Doc Should Contain Link    ${MODEL}
    ...    third level
    ...    Third%20level
    ...    Third level section
    Doc Should Contain Link    ${MODEL}[keywords][2]
    ...    Second LEVEL
    ...    Second%20level
    ...    Second level section
    Doc Should Contain    ${MODEL}    <h3 id="Second level">Second level</h3>
    Doc Should Contain    ${MODEL}    <h4 id="Third level">Third level</h4>

Only headers in introduction are linkable
    [Documentation]    Starting from RF 7.5 all headers get id, though.
    [Template]    NONE
    Doc Should Contain Name    ${MODEL}[keywords][2]    not linkable
    Doc Should Contain         ${MODEL}[keywords][2]    <h2 id="Not linkable">Not linkable</h2>

Special characters are percent encoded
    ${MODEL}[keywords][0]
    ...    Percent encoding: !"#%/()=?|+-_.!~*'()
    ...    Percent%20encoding%3A%20!%22%23%25%2F()%3D%3F%7C%2B-_.!~*'()
    ...    Percent encoding: !&quot;#%/()=?|+-_.!~*'() section

HTML entities are escaped also in name
    ${MODEL}[keywords][0]
    ...    HTML entities: &amp;&lt;&gt;
    ...    HTML%20entities%3A%20%26%3C%3E
    ...    HTML entities: &amp;&lt;&gt; section

Non-ASCII is encoded
    ${MODEL}[keywords][0]
    ...    Non-ASCII: ä\u2603
    ...    Non-ASCII%3A%20%C3%A4%E2%98%83
    ...    Non-ASCII: ä☃ section

*** Keywords ***
Doc Should Contain Link
    [Arguments]    ${object}    ${text}    ${target}    ${title}
    Doc Should Contain    ${object}    <a href="#${target}" title="${title}" class="name">${text}</a>

Doc Should Contain Name
    [Arguments]    ${object}    ${text}
    Doc Should Contain    ${object}    <span class="name">${text}</span>

Doc Should Contain
    [Arguments]    ${object}    ${text}
    Should Contain    ${object}[doc]    ${text}
