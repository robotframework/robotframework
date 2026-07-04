*** Settings ***
Suite Setup       Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/DocStringParsing.py
Resource          libdoc_resource.robot

*** Test Cases ***
Keyword Doc
    Should Be Equal Multiline    ${MODEL}[keywords][0][doc]    <p>Keyword with different argument and docstring.</p>
    ...    <p>This is second paragraph.</p>
    ...    <p>Here is more text in the docstring after the argument.</p>
    ...    <p>This ends the docstring.</p>

Keyword Arguments Doc
    Should Be Equal Multiline    ${MODEL}[keywords][0][args][0][doc]    <p>Documentation at same line</p>
    Should Be Empty    ${MODEL}[keywords][0][args][1][doc]
    Should Be Equal Multiline    ${MODEL}[keywords][0][args][2][doc]    <p>With a long description that spans multiple lines</p>
    ...    <p>def keyword(arg, *, kwonly, **kwargs) -&gt; str: pass</p>
    Should Be Equal Multiline    ${MODEL}[keywords][0][args][3][doc]    <p>Documentation at next line</p>

Keyword Return Doc
    Should Be Equal Multiline    ${MODEL}[keywords][0][returnDoc]    <p>This documentation for the return value</p>

Keyword Doc Not Existing Args Doc
    Should Be Equal Multiline    ${MODEL}[keywords][1][doc]    <p><b>Creating keyword failed:</b> Documentation given to non-existing argument 'does_not_exist'.</p>

Keyword Doc Not Existing Args Arguments Doc
    Should Be Empty    ${MODEL}[keywords][1][args][0][doc]
    Should Be Empty    ${MODEL}[keywords][1][args][1][doc]
