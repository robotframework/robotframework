*** Settings ***
Resource          libdoc_resource.robot
Suite Setup       Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/module.py
Test Template     Should Be Equal Multiline

*** Test Cases ***
Name
    ${MODEL}[name]          module

Documentation
    ${MODEL}[doc]           <p>Module test library.</p>

Version
    ${MODEL}[version]       0.1-alpha

Generated
    [Template]    Should Match Regexp
    ${MODEL}[generated]     \\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:\\d{2}

Scope
    ${MODEL}[scope]         GLOBAL

Inits
    [Template]    Should Be Empty
    ${MODEL}[inits]

Keyword Names
    ${MODEL}[keywords][0][name]     Get Hello
    ${MODEL}[keywords][1][name]     Keyword
    ${MODEL}[keywords][12][name]    Set Name Using Robot Name Attribute

Keyword Arguments
    [Template]    Verify Argument Models
    ${MODEL}[keywords][0][args]
    ${MODEL}[keywords][1][args]     a1=d    *a2
    ${MODEL}[keywords][6][args]     arg=hyv\\xe4
    ${MODEL}[keywords][9][args]     arg=hyvä
    ${MODEL}[keywords][10][args]    a=1    b=True    c=(1, 2, None)
    ${MODEL}[keywords][11][args]    arg=\\ robot \\ escapers\\n\\t\\r \\ \\
    ${MODEL}[keywords][12][args]    a    b    *args    **kwargs

Embedded Arguments
    [Template]    NONE
    Should Be Equal    ${MODEL}[keywords][13][name]    Takes \${embedded} \${args}
    Should Be Empty    ${MODEL}[keywords][13][args]

Keyword Documentation
    ${MODEL}[keywords][1][doc]
    ...    <p>A keyword.</p>
    ...    <p>See <a href="#Get%20Hello" class="name">get hello</a> for details.</p>
    ${MODEL}[keywords][0][doc]
    ...    <p>Get hello.</p>
    ...    <p>See <a href="#Importing" class="name">importing</a> for explanation of nothing and <a href="#Introduction" class="name">introduction</a> for no more information.</p>
    ${MODEL}[keywords][5][doc]
    ...    <p>This is short doc. It can span multiple physical lines and contain <b>formatting</b>.</p>
    ...    <p>This is body. It can naturally also contain multiple lines.</p>
    ...    <p>And paragraphs.</p>

Non-ASCII Keyword Documentation
    ${MODEL}[keywords][7][doc]    <p>Hyvää yötä.</p>\n<p>Спасибо!</p>
    ${MODEL}[keywords][8][doc]    <p>Hyvää yötä.</p>

Keyword Short Doc
    ${MODEL}[keywords][0][shortdoc]    Get hello.
    ${MODEL}[keywords][1][shortdoc]    A keyword.
    ${MODEL}[keywords][7][shortdoc]    Hyvää yötä.
    ${MODEL}[keywords][8][shortdoc]    Hyvää yötä.

Keyword Short Doc Spanning Multiple Physical Lines
    ${MODEL}[keywords][5][shortdoc]    This is short doc. It can span multiple physical lines and contain *formatting*.

Keyword tags
    [Template]    Should Be Equal As Strings
    ${MODEL}[keywords][1][tags]    []
    ${MODEL}[keywords][2][tags]    ['1', 'one', 'yksi']
    ${MODEL}[keywords][3][tags]    ['2', 'kaksi', 'two']
    ${MODEL}[keywords][4][tags]    ['tag1', 'tag2']

User keyword documentation formatting
    [Setup]    Run Libdoc And Parse Model From HTML    ${TESTDATADIR}/resource.robot
    ${MODEL}[keywords][0][doc]    <p>$\{CURDIR}</p>
    ${MODEL}[keywords][1][doc]    <p><b>DEPRECATED</b> for some reason.</p>
    ${MODEL}[keywords][2][doc]
    ${MODEL}[keywords][10][doc]
    ...    <p>Hyvää yötä.</p>
    ...    <p>Спасибо!</p>
    ${MODEL}[keywords][8][doc]
    ...    <p>foo bar <a href="#kw" class="name">kw</a>.</p>
    ...    <p>FIRST <span class="name">\${a1}</span> alskdj alskdjlajd askf laskdjf asldkfj alsdkfj alsdkfjasldkfj END</p>
    ...    <p>SECOND askf laskdjf <i>asldkfj</i> alsdkfj alsdkfjasldkfj askf <b>laskdjf</b> END</p>
    ...    <p>THIRD asldkfj <a href="#Introduction" class="name">introduction</a> alsdkfj <a href="http://foo.bar">http://foo.bar</a> END</p>
    ...    <ul>
    ...    <li>aaa</li>
    ...    <li>bbb</li>
    ...    </ul>
    ...    <hr>
    ...    <table border="1">
    ...    <tr>
    ...    <th>first</th>
    ...    <th>second</th>
    ...    </tr>
    ...    <tr>
    ...    <td>foo</td>
    ...    <td>bar</td>
    ...    </tr>
    ...    </table>

Private user keyword should be included
    [Setup]    Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/resource.robot
    ${MODEL}[keywords][-1][name]                 Private
    ${MODEL}[keywords][-1][tags]                 ['robot:private']
    ${MODEL}[keywords][-1][private]              True
    ${MODEL['keywords'][0].get('private')}       None

Deprecation
    [Setup]    Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/Deprecation.py
    ${MODEL}[keywords][0][deprecated]            True
    ${MODEL}[keywords][1][deprecated]            True
    ${MODEL['keywords'][2].get('deprecated')}    None
    ${MODEL['keywords'][3].get('deprecated')}    None

*** Keywords ***
Verify Argument Models
    [Arguments]    ${arg_models}    @{expected_reprs}
    [Tags]    robot: continue-on-failure
    Should Be True    len(${arg_models}) == len(${expected_reprs})
    FOR    ${arg_model}    ${expected_repr}    IN ZIP    ${arg_models}    ${expected_reprs}
        Verify Argument Model    ${arg_model}    ${expected_repr}    json=True
    END
