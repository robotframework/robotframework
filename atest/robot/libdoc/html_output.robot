*** Settings ***
Resource          libdoc_resource.robot
Suite Setup       Run Libdoc And Parse Model From HTML    ${TESTDATADIR}/module.py
Test Template     Should Be Equal

*** Test Cases ***
Name
    ${MODEL['name']}          module

Documentation
    ${MODEL['doc']}           <p>Module test library.</p>

Version
    ${MODEL['version']}       0.1-alpha

Generated
    [Template]    Should Match Regexp
    ${MODEL['generated']}     \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}

Scope
    ${MODEL['scope']}         global

Named Args
    ${MODEL['named_args']}    ${True}

Inits
    [Template]    Should Be Empty
    ${MODEL['inits']}

Keyword Names
    ${MODEL['keywords'][0]['name']}     Get Hello
    ${MODEL['keywords'][1]['name']}     Keyword
    ${MODEL['keywords'][13]['name']}    Set Name Using Robot Name Attribute

Keyword Arguments
    [Template]    Should Be Equal As Strings
    ${MODEL['keywords'][0]['args']}     []
    ${MODEL['keywords'][1]['args']}     ['a1=d', '*a2']
    ${MODEL['keywords'][6]['args']}     ['arg=hyv\\\\xe4']
    ${MODEL['keywords'][10]['args']}    ['arg=hyvä']
    ${MODEL['keywords'][12]['args']}    ['a=1', 'b=True', 'c=(1, 2, None)']
    ${MODEL['keywords'][13]['args']}    ['a', 'b', '*args', '**kwargs']

Embedded Arguments
    [Template]    NONE
    Should Be Equal    ${MODEL['keywords'][14]['name']}    Takes \${embedded} \${args}
    Should Be Empty    ${MODEL['keywords'][14]['args']}

Keyword Documentation
    ${MODEL['keywords'][1]['doc']}    <p>A keyword.</p>\n<p>See <a href="#Get%20Hello" class="name">get hello</a> for details.</p>
    ${MODEL['keywords'][0]['doc']}    <p>Get hello.</p>\n<p>See <a href="#Importing" class="name">importing</a> for explanation of nothing and <a href="#Introduction" class="name">introduction</a> for no more information.</p>
    ${MODEL['keywords'][5]['doc']}    <p>This is short doc. It can span multiple physical lines.</p>\n<p>This is body. It can naturally also contain multiple lines.</p>\n<p>And paragraphs.</p>

Non-ASCII Keyword Documentation
    ${MODEL['keywords'][8]['doc']}     <p>Hyvää yötä.</p>
    ${MODEL['keywords'][11]['doc']}    <p>Hyvää yötä.</p>\n<p>Спасибо!</p>

Keyword Short Doc
    ${MODEL['keywords'][1]['shortdoc']}     A keyword.
    ${MODEL['keywords'][0]['shortdoc']}     Get hello.
    ${MODEL['keywords'][8]['shortdoc']}     Hyvää yötä.
    ${MODEL['keywords'][11]['shortdoc']}    Hyvää yötä.

Keyword Short Doc Spanning Multiple Physical Lines
    ${MODEL['keywords'][5]['shortdoc']}    This is short doc. It can span multiple physical lines.

Keyword tags
    [Template]    Should Be Equal As Strings
    ${MODEL['keywords'][1]['tags']}    []
    ${MODEL['keywords'][2]['tags']}    ['1', 'one', 'yksi']
    ${MODEL['keywords'][3]['tags']}    ['2', 'kaksi', 'two']
    ${MODEL['keywords'][4]['tags']}    ['tag1', 'tag2']
