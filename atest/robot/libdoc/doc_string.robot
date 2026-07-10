*** Settings ***
Resource          libdoc_resource.robot

*** Variables ***
${LIBRARY}        ${TESTDATADIR}/DocStringParsing.py
${INXML}          ${OUTBASE}-2.xml
${INJSON}         ${OUTBASE}-2.json

*** Test Cases ***
Python to XML with HTML docs
    Run Libdoc And Parse Output    --spec-doc-format HTML ${LIBRARY}
    Validate XML Spec With HTML Docs

Python to XML with raw docs
    Run Libdoc And Parse Output    ${LIBRARY}
    Validate XML Spec With Raw Docs
    [Teardown]    Copy File    ${OUTXML}    ${INXML}

XML as input
    [Setup]    File Should Exist    ${INXML}
    Run Libdoc And Parse Output    ${INXML}
    Validate XML Spec With Raw Docs

Python to JSON with HTML docs
    Run Libdoc And Parse Model From JSON    ${LIBRARY}
    Validate JSON Spec With HTML Docs

Python to JSON with raw docs
    Run Libdoc And Parse Model From JSON    --spec-doc-format RAW ${LIBRARY}
    Validate JSON Spec With Raw Docs
    [Teardown]    Copy File    ${OUTJSON}    ${INJSON}

JSON as input
    [Setup]    File Should Exist    ${INJSON}
    Run Libdoc And Parse Model From JSON    ${INJSON}
    Validate JSON Spec With HTML Docs

Dynamic library as input
    Run Libdoc And Parse Output   ${TESTDATADIR}/DynamicLibrary.py::arg
    Validate XML Spec From Dynamic Library

*** Keywords ***
Validate XML Spec With HTML Docs
    Init Doc Should Be    0
    ...    ${EMPTY}
    Argument Doc Should Be    init    0    arg
    ...    <p>Documentation for <code>__init__</code> argument <code>arg</code>.</p>
    Keyword Doc Should Be     0
    ...    <p>Example with <em>everything</em>!</p>
    ...    <p>This is the second paragraph. We also have an indented
    ...    example:</p>
    ...    <div class="code"><pre><span></span><code>keyword(1, 2, kwonly=3, extra=4)
    ...    </code></pre></div>
    ...
    ...    <p>The end.</p>
    Argument Doc Should Be    0    0    own_line
    ...    <p>Documentation on same line.</p>
    Argument Doc Should Be    0    1    multiline
    ...    <p>Longer documentation that
    ...    spans multiple lines.</p>
    ...    <div class="code"><pre><span></span><code>Indentation is preserved.
    ...    </code></pre></div>
    Argument Doc Should Be    0    2    next_line
    ...    <p>Documentation on next line.</p>
    Argument Doc Should Be    0    3    empty_doc
    Return Doc Should Be      0
    ...    <p>Something useless.</p>
    ...    <p>On multiple lines
    ...    ${SPACE*8}with indentation.</p>
    Keyword Doc Should Be     1
    ...    <p><em>Creating keyword failed:</em> Documentation given to non-existing argument 'non_existing'.</p>
    Argument Doc Should Be    1    0    not_set
    Return Doc Should Be      1
    ...    <p>Zero</p>
    Raises Should Be          0
    ...    ValueError=<p>If something goes wrong.</p>
    ...    TypeError=<p>Should <em>not</em> happen.</p>
    Raises Should Be          1

Validate XML Spec With Raw Docs
    Init Doc Should Be    0
    ...    ${EMPTY}
    Argument Doc Should Be    init    0    arg
    ...    Documentation for `__init__` argument `arg`.
    Keyword Doc Should Be     0
    ...   Example with *everything*!
    ...
    ...   This is the second paragraph. We also have an indented
    ...   example:
    ...
    ...    ${SPACE*4}keyword(1, 2, kwonly=3, extra=4)
    ...
    ...   The end.
    Argument Doc Should Be    0    0    own_line
    ...    Documentation on same line.
    Argument Doc Should Be    0    1    multiline
    ...    Longer documentation that
    ...    spans multiple lines.
    ...
    ...    ${SPACE*4}Indentation is preserved.
    Argument Doc Should Be    0    2    next_line
    ...    Documentation on next line.
    Argument Doc Should Be    0    3    empty_doc
    Return Doc Should Be      0
    ...    Something useless.
    ...
    ...    On multiple lines
    ...    ${SPACE*8}with indentation.
    Keyword Doc Should Be     1
    ...    *Creating keyword failed:* Documentation given to non-existing argument 'non_existing'.
    Argument Doc Should Be    1    0    not_set
    Return Doc Should Be      1
    ...    Zero
    Raises Should Be          0
    ...    ValueError=If something goes wrong.
    ...    TypeError=Should *not* happen.
    Raises Should Be          1

Validate JSON Spec With HTML Docs
    Should Be Equal Multiline    ${MODEL}[inits][0][doc]
    Should Be Equal Multiline    ${MODEL}[inits][0][args][0][doc]
    ...    <p>Documentation for <code>__init__</code> argument <code>arg</code>.</p>
    Should Be Equal Multiline    ${MODEL}[keywords][0][doc]
    ...    <p>Example with <em>everything</em>!</p>
    ...    <p>This is the second paragraph. We also have an indented
    ...    example:</p>
    ...    <div class="code"><pre><span></span><code>keyword(1, 2, kwonly=3, extra=4)
    ...    </code></pre></div>
    ...
    ...    <p>The end.</p>
    Should Be Equal Multiline   ${MODEL}[keywords][0][args][0][doc]
    ...    <p>Documentation on same line.</p>
    Should Be Equal Multiline   ${MODEL}[keywords][0][args][1][doc]
    ...    <p>Longer documentation that
    ...    spans multiple lines.</p>
    ...    <div class="code"><pre><span></span><code>Indentation is preserved.
    ...    </code></pre></div>
    Should Be Equal Multiline   ${MODEL}[keywords][0][args][2][doc]
    ...    <p>Documentation on next line.</p>
    Should Be Equal Multiline   ${MODEL}[keywords][0][args][3][doc]
    Should Be Equal Multiline   ${MODEL}[keywords][0][returnDoc]
    ...    <p>Something useless.</p>
    ...    <p>On multiple lines
    ...    ${SPACE*8}with indentation.</p>
    Should Be Equal Multiline   ${MODEL}[keywords][1][doc]
    ...    <p><em>Creating keyword failed:</em> Documentation given to non-existing argument 'non_existing'.</p>
    Should Be Equal Multiline   ${MODEL}[keywords][1][args][0][doc]
    Should Be Equal Multiline   ${MODEL}[keywords][1][returnDoc]
    ...    <p>Zero</p>
    Length Should Be            ${MODEL}[keywords][0][raises]    2
    Length Should Be            ${MODEL}[keywords][1][raises]    0
    Should Be Equal Multiline   ${MODEL}[keywords][0][raises][ValueError]
    ...    <p>If something goes wrong.</p>
    Should Be Equal Multiline   ${MODEL}[keywords][0][raises][TypeError]
    ...    <p>Should <em>not</em> happen.</p>

Validate JSON Spec With Raw Docs
    Should Be Equal Multiline    ${MODEL}[inits][0][doc]
    Should Be Equal Multiline    ${MODEL}[inits][0][args][0][doc]
    ...    Documentation for `__init__` argument `arg`.
    Should Be Equal Multiline    ${MODEL}[keywords][0][doc]
    ...   Example with *everything*!
    ...
    ...   This is the second paragraph. We also have an indented
    ...   example:
    ...
    ...    ${SPACE*4}keyword(1, 2, kwonly=3, extra=4)
    ...
    ...   The end.
    Should Be Equal Multiline   ${MODEL}[keywords][0][args][0][doc]
    ...    Documentation on same line.
    Should Be Equal Multiline   ${MODEL}[keywords][0][args][1][doc]
    ...    Longer documentation that
    ...    spans multiple lines.
    ...
    ...    ${SPACE*4}Indentation is preserved.
    Should Be Equal Multiline   ${MODEL}[keywords][0][args][2][doc]
    ...    Documentation on next line.
    Should Be Equal Multiline   ${MODEL}[keywords][0][args][3][doc]
    Should Be Equal Multiline   ${MODEL}[keywords][0][returnDoc]
    ...    Something useless.
    ...
    ...    On multiple lines
    ...    ${SPACE*8}with indentation.
    Should Be Equal Multiline   ${MODEL}[keywords][1][doc]
    ...    *Creating keyword failed:* Documentation given to non-existing argument 'non_existing'.
    Should Be Equal Multiline   ${MODEL}[keywords][1][args][0][doc]
    Should Be Equal Multiline   ${MODEL}[keywords][1][returnDoc]
    ...    Zero
    Length Should Be            ${MODEL}[keywords][0][raises]    2
    Length Should Be            ${MODEL}[keywords][1][raises]    0
    Should Be Equal Multiline   ${MODEL}[keywords][0][raises][ValueError]
    ...    If something goes wrong.
    Should Be Equal Multiline   ${MODEL}[keywords][0][raises][TypeError]
    ...    Should *not* happen.

Validate XML Spec From Dynamic Library
    Init Doc Should Be    0
    ...    Dummy documentation for `__init__`.
    Argument Doc Should Be    init    0    arg1
    ...    Doc for `arg1`.
    Argument Doc Should Be    init    1    arg2
    ...    Doc for `arg2`.
    Keyword Doc Should Start With    6
    ...    Dummy documentation for `Keyword-only args`.
    ...
    ...    Neither `Keyword 1` or `KW 2` do anything really interesting.
    Argument Doc Should Be    6    0    ${EMPTY}
    Argument Doc Should Be    6    1    kwo
    ...    Doc for `kwo`.
    Argument Doc Should Be    6    2    another
    ...    Doc for `another`.
